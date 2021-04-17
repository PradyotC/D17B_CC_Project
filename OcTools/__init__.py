import owncloud


class OcTools(object):
    oc = owncloud.Client('http://34.123.27.121/')
    oc.login('user', 'q5XLTik5OPYm')

    def __init__(self, threshold):
        self.threshold = threshold

    def shareFile(self, username, filepath):
        if self.fileExists(filepath):
            oc = self.oc
            _, p = self.isFolder(filepath)
            bool1, path, links, c = self.checkDuplicateExist(filepath)
            if bool1:
                if links < self.threshold:
                    oc.share_file_with_user(path, username)
                elif links == self.threshold:
                    path = self.duplicateFilepath(p, c + 1)
                    oc.copy(p, path)
                    oc.share_file_with_user(path, username)
            else:
                path = self.duplicateFilepath(p, 1)
                oc.copy(p, path)
                oc.share_file_with_user(path, username)
            return {'message': 'File shared successfully', 'path': path}
        else:
            return {'message': 'File does not exist'}

    def fileExists(self, filepath):
        oc = self.oc
        try:
            oc.file_info(filepath)
            return True
        except Exception as e:
            if str(e)[-3:] == "404":
                return False

    def isFolder(self, filepath):
        oc = self.oc
        return oc.file_info(filepath).is_dir(), oc.file_info(filepath).path

    def duplicatePath(self, filepath):
        cond1, path1 = self.isFolder(filepath)
        if cond1:
            newpath = path1[:-1] + 'Duplicates/'
        else:
            newpath = path1 + 'Duplicates/'
        return newpath

    def duplicateFilepath(self, filepath, count):
        cond1, path1 = self.isFolder(filepath)
        if cond1:
            k = path1[:-1].rfind('/') + 1
            newpath = path1[:-1] + 'Duplicates/' + path1[k:-1] + '_' + str(count) + '/'
        else:
            k = path1.rfind('/') + 1
            r = path1.rfind('.')
            newpath = path1 + 'Duplicates/' + path1[k:r] + '_' + str(count) + path1[r:]
        return newpath

    def checkDuplicateExist(self, filepath):
        oc = self.oc
        try:
            y = oc.list(self.duplicatePath(filepath))
            list1 = []
            for z in y:
                l1 = z.get_name().rfind('_') + 1
                if z.is_dir():
                    list1.append(int(z.get_name()[l1:]))
                else:
                    r = z.get_name().rfind('.')
                    list1.append(int(z.get_name()[l1:r]))
            m = max(list1)
            checkPath = self.duplicateFilepath(filepath, m)
            leng = len(oc.get_shares(checkPath))
            return True, checkPath, leng, m
        except Exception as e:
            if str(e)[-3:] == "404":
                oc.mkdir(self.duplicatePath(filepath))
                checkPath = self.duplicateFilepath(filepath, 1)
                return False, checkPath, 0, 0
