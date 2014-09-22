import sublime
import sublime_plugin
import os


class SftpUploadListCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        sel = self.view.sel()
        window = view.window()
        folders = window.folders()

        regions = []
        if sel[0].empty():
            buffer_region = sublime.Region(0, view.size())
            regions = view.split_by_newlines(buffer_region)
        else:
            regions = [r for r in sel]

        file_list = [view.substr(r).strip() for r in regions]

        def confirm_folder(index):
            if (index != -1):
                self.upload_from_folder(folders[index], file_list)

        if (len(folders) > 1):
            self.show_quick_panel(folders, confirm_folder)
        else:
            if folders:
                self.upload_from_folder(folders[0], file_list)
            else:
                sublime.error_message('At least one folder must be present in your project.')

    def upload_from_folder(self, folder, file_list):
        window = self.view.window()
        paths = []
        errors = []
        for relative_path in file_list:
            path = folder.rstrip(os.sep) + os.sep + relative_path.lstrip(os.sep)
            if not os.path.exists(path):
                errors.append('File {0} does not exist.'.format(path))
            else:
                paths.append(path)

        if errors:
            # In case of errors, do not upload anything.
            # In this way the user is sure that every file exists
            # when the upload process begins.
            sublime.error_message('\n\n'.join(errors))
            return

        def confirm_upload(index):
            # -1: cancel, 0: do nothing. 1: upload
            if index == 1:
                window.run_command('sftp_upload_file', {'paths': paths})

        self.show_quick_panel([["No", "Do nothing"],
                                ["Yes", "Upload {0} files".format(len(paths))]],
                                confirm_upload)

    # Helper method to call show_quick_panel without throwing errors.
    # In ST3 subsequent calls to show_quick_panel will raise a "Quick panel unavailable" error.
    # See http://www.sublimetext.com/forum/viewtopic.php?f=6&t=10999
    def show_quick_panel(self, options, done):
        sublime.set_timeout(lambda: self.view.window().show_quick_panel(options, done), 10)
