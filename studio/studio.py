import asyncio
import json
import os
import os.path
import re
import shutil
import sys
from pathlib import Path
from string import Template
from subprocess import PIPE, STDOUT, Popen
import time
from urllib.parse import urlparse
import zipfile
import file_utils

from h2o_wave import Q, app, main, ui

project_dir = 'project'
_server_adress = os.environ.get('H2O_WAVE_ADDRESS', 'http://127.0.0.1:10101')
_app_host = urlparse(os.environ.get('H2O_WAVE_APP_ADDRESS', 'http://127.0.0.1:8000')).hostname
_app_port = '10102'
vsc_extension_path = os.path.join('..', 'tools', 'vscode-extension')
main_app_file = os.path.join(project_dir, 'app.py')


def start(filename: str, is_app: bool):
    env = os.environ.copy()
    env['H2O_WAVE_BASE_URL'] = os.environ.get('H2O_WAVE_BASE_URL', '/')
    env['H2O_WAVE_ADDRESS'] = _server_adress
    env['PYTHONUNBUFFERED'] = 'False'
    # The environment passed into Popen must include SYSTEMROOT, otherwise Popen will fail when called
    # inside python during initialization if %PATH% is configured, but without %SYSTEMROOT%.
    if sys.platform.lower().startswith('win'):
        env['SYSTEMROOT'] = os.environ['SYSTEMROOT']
    if is_app:
        env['H2O_WAVE_APP_ADDRESS'] = f'http://{_app_host}:{_app_port}'
        return Popen([
            sys.executable, '-m', 'uvicorn',
            '--host', '0.0.0.0',
            '--port', _app_port,
            f'{filename.replace(".py", "")}:main',
        ], env=env, stdout=PIPE, stderr=STDOUT)
    else:
        return Popen([sys.executable, filename], env=env, stdout=PIPE, stderr=STDOUT)

async def stop_previous(q: Q) -> None:
    # Stop script if any.
    if not q.user.is_app and q.user.active_path:
        demo_page = q.site[q.user.active_path]
        demo_page.drop()
        await demo_page.save()
    # Stop app if any.
    if q.user.wave_process and q.user.wave_process.returncode is None:
        q.user.wave_process.terminate()
        q.user.wave_process.wait()
    if q.user.display_logs_future:
        q.user.display_logs_future.cancel()

async def setup_page(q: Q):
    py_content = ''
    # In prod.
    if os.path.exists('autocomplete_parser.py') and os.path.exists('autocomplete_utils.py'):
        py_content = file_utils.read_file('autocomplete_parser.py')
        py_content += file_utils.read_file('autocomplete_utils.py')
    # When run in development from Wave repo.
    elif os.path.exists(vsc_extension_path):
        py_content = file_utils.read_file(os.path.join(vsc_extension_path, 'server', 'parser.py'))
        py_content += file_utils.read_file(os.path.join(vsc_extension_path, 'server', 'utils.py'))
    if py_content:
        py_content += file_utils.read_file('autocomplete.py')
    template = Template(file_utils.read_file('studio.js')).substitute(
        snippets1=q.app.snippets1,
        snippets2=q.app.snippets2,
        file_content=file_utils.read_file(main_app_file) or '',
        py_content=py_content,
        folder=json.dumps(file_utils.get_file_tree(project_dir)),
    )
    q.page['meta'] = ui.meta_card(
        box='',
        title='Wave Studio',
        scripts=[
            ui.script('https://cdn.jsdelivr.net/pyodide/v0.20.0/full/pyodide.js'),
            ui.script('https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.33.0/min/vs/loader.min.js'),
            ui.script('https://unpkg.com/vue@3.1.1/dist/vue.global.prod.js'),
        ],
        script=ui.inline_script(content=template, requires=['require', 'Vue'], targets=['monaco-editor']),
        stylesheets=[ui.stylesheet(f'/assets/studio.css?version={time.time()}')], # Cache busting.
        layouts=[
            ui.layout(breakpoint='xs', zones=[
                ui.zone('header'),
                ui.zone('main', size='calc(100vh - 80px)', direction=ui.ZoneDirection.ROW),
            ])
        ])
    q.page['header'] = ui.header_card(
        box='header',
        title='Wave Studio',
        subtitle='Develop Wave apps completely in browser',
        image='https://wave.h2o.ai/img/h2o-logo.svg',
        items=[
            ui.button(name='console', label='Console', icon='CommandPrompt'),
            ui.button(name='open_preview', label='Preview', icon='OpenInNewWindow'),
            ui.dropdown(name='dropdown', width='170px', trigger=True, value=(q.user.view or 'split'), choices=[
                ui.choice(name='split', label='Split view'),
                ui.choice(name='code', label='Full code view'),
                ui.choice(name='preview', label='Full preview view'),
            ]),
            ui.button(name='import_project', label='Import', icon='Upload'),
            ui.button(name='export_project', label='Export', icon='Download'),
        ]
    )
    editor_html = '''
<div id="editor">
  <div id="files">
    <div id="file-tree"></div>
    <div id="file-tree-menu"></div>
  </div>
  <div id="monaco-editor"></div>
</div>
    '''
    q.page['logs'] = ui.markdown_card(box=ui.box('main', width='0px'), title='Logs', content='')
    q.page['code'] = ui.markup_card(box=ui.box('main', width='100%'), title='', content=editor_html)
    show_empty_preview(q)

def show_empty_preview(q: Q):
    del q.page['preview']
    q.page['preview'] = ui.tall_info_card(
        box=ui.box('main', width=('0px' if q.user.view == "code" else '100%')),
        name='',
        image='/assets/app_not_running.svg',
        image_height='500px',
        title='Oops! There is no running app.',
        caption='Try writing one in the code editor on the left.'
    )

async def display_logs(q: Q) -> None:
  lines = []
  p = q.user.wave_process
  os.set_blocking(p.stdout.fileno(), False)
  while True:
      line = p.stdout.readline() 
      if line:
          lines.append(line.decode('utf8')) 
          code = ''.join(lines)
          q.page['logs'].content = f'```\n{code}\n```'
          q.page['meta'].script = ui.inline_script('scrollLogsToBottom()')
          await q.page.save()
      else:
          await q.sleep(0.5)

async def render_code(q: Q):
    if q.events.editor:
        code = file_utils.pythonify_js_code(q.events.editor.change if q.events.editor else '')
        with open(q.client.open_file, 'w') as f:
            f.write(code)
    else:
        code = file_utils.read_file(q.client.open_file)

    path = ''
    if q.client.open_file == main_app_file:
        app_match = re.search('\n@app\(.*(\'|\")(.*)(\'|\")', code)
        if app_match:
            path = app_match.group(2)
            q.user.is_app = True
        else:
            script_match = re.search('site\[(\'|\")(.*)(\'|\")\]', code)
            if script_match:
                path = script_match.group(2)
                q.user.is_app = False
        if not path:
            show_empty_preview(q)
            q.user.is_app = False
            return
        q.user.active_path = path

    await stop_previous(q)
    exec_file = main_app_file.replace(os.sep, '.') if q.user.is_app else main_app_file
    q.user.wave_process = start(exec_file, q.user.is_app)
    q.user.display_logs_future = asyncio.ensure_future(display_logs(q))
    del q.page['empty']

    q.page['preview'] = ui.frame_card(
        box=ui.box('main', width=('0px' if q.user.view == 'code' else '100%')),
        title=f'Preview of {_server_adress}{path}',
        path=f'{_server_adress}{path}'
    )
    q.page['header'].items[1].button.disabled = False
    q.page['header'].items[1].button.path = f'{_server_adress}{path}'

def update_file_tree(q: Q) -> None:
    q.page['meta'].script = ui.inline_script(f'eventBus.emit("folder", {json.dumps(file_utils.get_file_tree(project_dir))})')

def open_editor_file(q: Q, file: str) -> None:
    q.page['meta'].script = ui.inline_script(f'editor.setValue(`{file_utils.read_file(file)}`)')

async def on_startup():
    file_utils.create_folder(project_dir)
    app_path = Path(main_app_file)
    if not app_path.exists():
        shutil.copy('starter.py', app_path)

async def on_shutdown():
    file_utils.remove_folder(project_dir)

async def export(q: Q):
    shutil.make_archive('app', 'zip', '.', project_dir)
    q.app.zip_path, = await q.site.upload(['app.zip'])
    q.page["meta"].script = ui.inline_script(f'window.open("{q.app.zip_path}", "_blank");')
    os.remove("app.zip")

@app('/studio', on_startup=on_startup, on_shutdown=on_shutdown)
async def serve(q: Q):
    global project_dir
    global main_app_file
    if not q.app.initialized:
        # TODO: Serve snippets directly from static dir.
        # Prod.
        if os.path.exists('base-snippets.json') and os.path.exists('component-snippets.json'):
            q.app.snippets1, q.app.snippets2, = await q.site.upload(['base-snippets.json', 'component-snippets.json'])
        # When run in development from Wave repo.
        elif os.path.exists(vsc_extension_path):
            q.app.snippets1, q.app.snippets2, = await q.site.upload([
                os.path.join(vsc_extension_path, 'base-snippets.json'),
                os.path.join(vsc_extension_path, 'component-snippets.json')
            ])
        q.app.initialized = True
    if not q.client.initialized:
        await setup_page(q)
        q.client.open_file = main_app_file
        q.client.initialized = True
        await render_code(q)

    if q.args.dropdown:
        q.user.view = q.args.dropdown
        q.page['header'].items[3].dropdown.value = q.args.dropdown
    if q.args.export_project:
        await export(q)
    elif q.args.import_project:
        q.page['meta'].dialog = ui.dialog(name='dialog', title='Import Project', events=['dismissed'], closable=True, items=[
            ui.message_bar(type='warning', text='Current project files will be replaced with uploaded content.'),
            ui.file_upload(name='imported_project', file_extensions=['zip']),		
        ])
    elif q.args.imported_project:
        zip_path = await q.site.download(q.args.imported_project[0], os.getcwd())
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            root_dirs = [f for f in zip_ref.filelist if f.is_dir() and f.filename.count(os.path.sep) == 1]
            if len(root_dirs) == 1:
                file_utils.remove_folder(project_dir)
                zip_ref.extractall()
                file_utils.remove_file(zip_path)
                q.page['meta'].dialog = None
                q.page['meta'].notification_bar = ui.notification_bar(
                    name='notification',
                    text='Project imported successfully!',
                    type='success',
                    position='top-right',
                    events=['dismissed'],
                )
                project_dir = root_dirs[0].filename.replace(os.path.sep, '')
                main_app_file = file_utils.find_main_file(project_dir)
                q.client.open_file = main_app_file
                await render_code(q)
                update_file_tree(q)
                await q.page.save()
                open_editor_file(q, main_app_file)
            else:
                q.page['meta'].dialog.items = [
                    ui.message_bar(type='error', text='There must be exactly 1 root folder.'),
                    ui.button(name='import_project', label='Import again', icon='Upload'),
                ]
    elif q.args.dropdown == 'code':
        q.page['preview'].box = ui.box('main', width='0px')
        q.page['code'].box = ui.box('main', width='100%')
    elif q.args.dropdown == 'split':
        q.page['preview'].box = ui.box('main', width='100%')
        q.page['code'].box = ui.box('main', width='100%')
    elif q.args.dropdown == 'preview':
        q.page['preview'].box = ui.box('main', width='100%')
        q.page['code'].box = ui.box('main', width='0px')
    elif q.args.console:
        q.page['preview'].box = ui.box('main', width='100%')
        q.page['code'].box = ui.box('main', width='0px')
        q.page['logs'].box = ui.box('main', width='100%')
        q.page['header'].items[0].button.name = 'show_code'
        q.page['header'].items[0].button.label = 'Code'
        q.page['header'].items[0].button.icon = 'Code'
    elif q.args.show_code:
        q.page['preview'].box = ui.box('main', width='100%')
        q.page['logs'].box = ui.box('main', width='0px')
        q.page['code'].box = ui.box('main', width='100%')
        q.page['header'].items[0].button.name = 'console'
        q.page['header'].items[0].button.label = 'Console'
        q.page['header'].items[0].button.icon = 'CommandPrompt'

    if q.events.editor:
        await render_code(q)
    elif q.events.dialog and q.events.dialog.dismissed:
        q.page['meta'].dialog = None
    elif q.events.notification and q.events.notification.dismissed:
        q.page['meta'].notification_bar = None
    elif q.events.file_viewer:
        e = q.events.file_viewer
        if e.new_file:
            file_utils.create_file(os.path.join(e.new_file['path'], e.new_file['name']))
        elif e.new_folder:
            file_utils.create_folder(os.path.join(e.new_folder['path'], e.new_folder['name']))
        elif e.remove_file:
            file_utils.remove_file(e.remove_file)
        elif e.remove_folder:
            file_utils.remove_folder(e.remove_folder)
        elif e.rename:
            file_utils.rename(e.rename['path'], e.rename['name'])
        elif e.open:
            q.client.open_file = e.open
            open_editor_file(q, e.open)
            await q.page.save()
        update_file_tree(q)

    await q.page.save()