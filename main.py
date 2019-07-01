import subprocess

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction


class VboxExtension(Extension):
    def __init__(self):
        super(VboxExtension, self).__init__()
        self.vms = None
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

    def load_vms(self):
        self.vms = vbox_vms()

    def build_result(self, vm):
        if vm['running']:
            cmd = 'vboxmanage controlvm "{}" acpipowerbutton'
        else:
            cmd = 'vboxmanage startvm "{}" --type gui'

        return ExtensionResultItem(icon='images/icon.png',
                                   name=vm['name'].decode('utf-8'),
                                   description=vm['description'],
                                   on_enter=RunScriptAction(cmd.format(vm['id']), None))


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        vms = []
        arg = event.get_argument()

        if extension.vms is None or arg is None:
            extension.load_vms()

        vms = extension.vms

        if arg is not None:
            arg = arg.lower()
            vms = [v for v in vms if arg in v['name']]

        return RenderResultListAction(list(map(extension.build_result, vms)))


def vbox_vms():
    vms = vboxmanage_list('vms')
    running_vms = vboxmanage_list('runningvms')

    for id, vm in running_vms.items():
        vms[id]['running'] = True
        vms[id]['description'] = 'Stop'

    return list(vms.values())


def vboxmanage_list(output):
    out = subprocess.check_output(['vboxmanage', 'list', output])
    vms = {}

    for l in out.splitlines():
        name, id = l.rsplit(b' ', 1)
        vms[id] = {
            'id': id,
            'name': name[1:-1],
            'running': False,
            'description': 'Start'
        }

    return vms


if __name__ == '__main__':
    VboxExtension().run()
