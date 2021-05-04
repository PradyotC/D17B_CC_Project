import owncloud
import numpy as np

class OcTools(object):
    oc = owncloud.Client('http://34.123.27.121/')
    oc.login('user', 'q5XLTik5OPYm')

    def __init__(self, threshold):
        self.threshold = threshold

    def ocUser(self, username, userpasswrd):
        ocu = owncloud.Client('http://34.123.27.121/')
        ocu.login(username, userpasswrd)
        return ocu

    def shareWithUser(self, path, username, userpasswrd):
        oc = self.oc
        ocu = self.ocUser(username,userpasswrd)
        dirListLength,dirList = self.dirPathList(path)
        if dirListLength != 0:
            for x in dirList:
                if self.fileExists(ocu,x) == False:
                    ocu.mkdir(x)
        oc.share_file_with_user(path, username)
        if dirListLength != 0:
            truePathL = path.rfind('/')
            truePath = path[truePathL:]
            e = truePath.rfind('_')
            f = truePath.rfind('.')
            targetPath = dirList[dirListLength-1]
            ocu.move(truePath,targetPath[:-1]+truePath[:e]+truePath[f:])
        return targetPath[:-1]+truePath[:e]+truePath[f:]

    def fileExists(self, oc, filepath):
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

    def dirPathList(self, filepath):
        k = []
        l = filepath
        if l.rfind('/') != -1:
            last = l.rfind('/')
            while l.rfind('/') != 0:
                k.insert(0,l[:last+1])
                l = l[:last]
                last = l.rfind('/')
            k.pop()
        return len(k),k

    def checkDuplicateExist(self, filepath):
        oc = self.oc
        try:
            y = oc.list(self.duplicatePath(filepath))
            list1 = []
            for z in y:
                l1 = z.get_name().rfind('_') + 1
                if z.is_dir():
                    num1 = int(z.get_name()[l1:])
                    checkPath = self.duplicateFilepath(filepath, num1)
                    leng = len(oc.get_shares(checkPath))
                    thisList = [checkPath, leng, num1]
                    list1.append(thisList)
                else:
                    r = z.get_name().rfind('.')
                    num1 = int(z.get_name()[l1:r])
                    checkPath = self.duplicateFilepath(filepath, num1)
                    leng = len(oc.get_shares(checkPath))
                    thisList = [checkPath, leng, num1]
                    list1.append(thisList)
            return True, list1
        except Exception as e:
            if str(e)[-3:] == "404":
                list1 = []
                return False, list1

    def getDuplicateAttributes(self, filepath):
        isExist, dictList = self.checkDuplicateExist(filepath)
        if isExist:
            list2 = np.array(dictList)
            C = list2[:,1].astype('int64')
            val1 = np.argmin(C)
            list3 = dictList[val1]
            return True, str(list3[0]), int(list3[1]), int(list3[2])
        else:
            checkPath = self.duplicateFilepath(filepath, 1)
            return False, checkPath, 0, 0

    def shareFile(self, username, userpasswrd, filepath):
        if self.fileExists(self.oc,filepath):
            oc = self.oc
            _, p = self.isFolder(filepath)
            bool1, path, links, c = self.getDuplicateAttributes(filepath)
            if bool1:
                if links < self.threshold:
                    path1 = self.shareWithUser(path, username, userpasswrd)
                elif links == self.threshold:
                    path = self.duplicateFilepath(p, c + 1)
                    oc.copy(p, path)
                    path1 = self.shareWithUser(path, username, userpasswrd)
            else:
                oc.mkdir(self.duplicatePath(filepath))
                path = self.duplicateFilepath(p, 1)
                oc.copy(p, path)
                path1 = self.shareWithUser(path, username, userpasswrd)
            return {'message': 'File shared successfully', 'path': path1}
        else:
            return {'message': 'File does not exist'}

    def modifyFile(self, filepath, filecontents):
        if self.fileExists(self.oc,filepath):
            oc = self.oc
            bool1, p = self.isFolder(filepath)
            if bool1:
                return {'message': 'Given Path is a Folder and not a file'}
            else:
                str1 = filecontents
                str2 = bytes(str1, 'UTF-8')
                oc.put_file_contents(p, str2)
                bool2, duplicateFileList = self.checkDuplicateExist(filepath)
                if bool2:
                    for iterations in duplicateFileList:
                        duplicateFilePath1 = iterations[0]
                        oc.put_file_contents(duplicateFilePath1, str2)
                    return {'message': 'File modified successfully and duplicates updated'}
                else:
                    return {'message': 'File modified successfully'}
        else:
            return {'message': 'File does not exist'}