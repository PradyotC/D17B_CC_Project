import owncloud
import base64

class OcTools(object):
    oc = owncloud.Client('http://34.123.27.121/')
    oc.login('user', 'q5XLTik5OPYm')

    def __init__(self, threshold):
        self.threshold = threshold

    def ocUser(self, username, userpasswrd):
        ocu = owncloud.Client('http://34.123.27.121/')
        ocu.login(username, userpasswrd)
        return ocu

    def getTruePath(self, oc, filepath):
        p = oc.file_info(filepath).get_path()
        if not oc.file_info(filepath).is_dir():
            if p == '/':
                p = '/' + oc.file_info(filepath).get_name()
            else:
                p = p + '/' + oc.file_info(filepath).get_name()
        else:
            p = p + '/'
        return p

    def getUserInfo(self, userList):
        oc = self.oc
        userInfoList = []
        if self.fileExists(oc, '/.userInfo/'):
            y = oc.list('/.userInfo/')
            for i in y:
                r = i.get_name().rfind('.txt')
                userNameHex = i.get_name()[1:r]
                userName = bytes.fromhex(userNameHex).decode('utf-8')
                if userName in userList:
                    str1 = oc.get_file_contents(i.get_path()+'/'+i.get_name()).decode('UTF-8')
                    userInfoList.append(str1.split('\n'))
            return True, userInfoList
        else:
            return False, userInfoList

    def checkUserInfoFileEmpty(self):
        oc = self.oc
        if len(oc.list('/.userInfo/')) == 0:
            oc.delete('/.userInfo/')

    def createUserInfo(self, username, userpasswrd):
        oc = self.oc
        oc.create_user(username, userpasswrd)
        if self.fileExists(oc, '/.userInfo/') == False:
            oc.mkdir('/.userInfo/')
        usernameHex = username.encode('utf-8')
        userFile = '/.userInfo/a' + usernameHex.hex() + '.txt'
        infoData = bytes(username + '\n' + userpasswrd, 'UTF-8')
        oc.put_file_contents(userFile, infoData)
        return "User Created Sucessfully"

    def shareWithUser(self, path, p, username, userpasswrd):
        oc = self.oc
        ocu = self.ocUser(username, userpasswrd)
        dirListLength, dirList = self.dirPathList(p)
        if dirList:
            if dirList[0] == '/':
                print(dirListLength, dirList)
                dirList.pop()
                dirListLength = dirListLength - 1
        if dirListLength != 0:
            for x in dirList:
                if self.fileExists(ocu, x) == False:
                    ocu.mkdir(x)
        oc.share_file_with_user(path, username, perms=2)
        l1 = oc.get_shares(path)
        for i in l1:
            if i.get_share_with_displayname() == username:
                id1 = i.get_id()
                break
        if oc.file_info(path).is_dir():
            truePathL = path[:-1].rfind('/')
            truePath = path[truePathL:]
            ocu.move(truePath, p)
        else:
            truePathL = path.rfind('/')
            truePath = path[truePathL:]
            e = truePath.rfind('_')
            f = truePath.rfind('.')
            ocu.move(truePath, p)
        oc.update_share(id1, perms=1)
        return p

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
        if l.rfind('/') == (len(l)-1):
            l = l[:-1]
        if l.rfind('/') != -1:
            last = l.rfind('/')
            while l.rfind('/') != 0:
                k.insert(0, l[:last+1])
                l = l[:last]
                last = l.rfind('/')
        return len(k), k

    def checkDuplicate(self, filepath):
        oc = self.oc
        try:
            y = oc.list(self.duplicatePath(filepath))
            return True
        except Exception as e:
            if str(e)[-3:] == "404":
                return False

    def checkDuplicateExist(self, filepath):
        oc = self.oc
        try:
            y = oc.list(self.duplicatePath(filepath))
            list1 = []
            l3 = []
            for z in y:
                l1 = z.get_name().rfind('_') + 1
                if z.is_dir():
                    num1 = int(z.get_name()[l1:])
                    checkPath = self.duplicateFilepath(filepath, num1)
                    l1 = oc.get_shares(checkPath)
                    [l3.append([i.get_share_with_displayname(), i.get_id()]) for i in l1]
                    leng = len(l1)
                    thisList = [checkPath, leng, num1]
                    list1.append(thisList)
                else:
                    r = z.get_name().rfind('.')
                    num1 = int(z.get_name()[l1:r])
                    checkPath = self.duplicateFilepath(filepath, num1)
                    l1 = oc.get_shares(checkPath)
                    [l3.append([i.get_share_with_displayname(), i.get_id()]) for i in l1]
                    leng = len(l1)
                    thisList = [checkPath, leng, num1]
                    list1.append(thisList)
            return True, list1, l3
        except Exception as e:
            if str(e)[-3:] == "404":
                list1 = []
                return False, list1, list1

    def getDuplicateFileList(self, filepath):
        oc = self.oc
        l1 = self.dirPathList(filepath)
        l1List = list(l1)
        l1List[0] = l1List[0] + 1
        l1List[1].append(filepath)
        l1 = tuple(l1List)
        l2 = []
        for x in l1[1]:
            if self.checkDuplicate(x):
                y = len(x)
                for xx in self.column(self.checkDuplicateExist(x)[1],0):
                    l2.append(xx+filepath[y:])
                break
        if len(l2)!=0:
            return True, l2
        else:
            return False, l2

    def column(self, matrix, i):
        return [row[i] for row in matrix]

    def getDuplicateAttributes(self, filepath):
        isExist, dataList, _ = self.checkDuplicateExist(filepath)
        if isExist:
            C = self.column(dataList, 1)
            D = self.column(dataList, 2)
            val1 = C.index(min(C))
            val2 = max(D)
            list3 = dataList[val1]
            return True, str(list3[0]), int(list3[1]), val2
        else:
            checkPath = self.duplicateFilepath(filepath, 1)
            return False, checkPath, 0, 0

    def shareFile(self, username, userpasswrd, filepath):
        ocu = self.ocUser(username, userpasswrd)
        if self.fileExists(ocu,filepath):
            return {'message': 'File already shared'}
        else:    
            if self.fileExists(self.oc, filepath):
                oc = self.oc
                _, p = self.isFolder(filepath)
                bool1, path, links, c = self.getDuplicateAttributes(filepath)
                if bool1:
                    if links < self.threshold:
                        path1 = self.shareWithUser(path, p, username, userpasswrd)
                    elif links == self.threshold:
                        path = self.duplicateFilepath(p, c + 1)
                        oc.copy(p, path)
                        path1 = self.shareWithUser(path, p, username, userpasswrd)
                else:
                    oc.mkdir(self.duplicatePath(filepath))
                    path = self.duplicateFilepath(p, 1)
                    oc.copy(p, path)
                    path1 = self.shareWithUser(path, p, username, userpasswrd)
                return {'message': 'Shared successfull', 'path': path1}
            else:
                return {'message': 'File or Folder does not exist'}

    def createFile(self, filepath, type1, filecontents):
        if (not self.fileExists(self.oc, filepath)):
            oc = self.oc
            if type1=='file':
                str1 = filecontents
                str2 = bytes(str1, 'UTF-8')
            list1 = self.dirPathList(filepath)[1]
            list1.reverse()
            list2 = []
            list3 = []
            ogDirectory = '/'
            for i in list1:
                if (not self.fileExists(self.oc,i)):
                    list2.append('/'+i[1:])
                elif (not self.fileExists(self.oc,i)) and (not self.checkDuplicate(i)):
                    list2.append('/'+i[1:])
                else:
                    ogDirectory = i
                    break
            list2.reverse()
            list4 = []
            [list4.append(i[len(ogDirectory)-1:]) for i in list2]
            list2 = list4
            list2.append(filepath[len(ogDirectory)-1:])
            if ogDirectory!="/":
                list3 = self.column(self.checkDuplicateExist(ogDirectory)[1],0)
            list3.insert(0, ogDirectory)
            for j in list3:
                for k in list2:
                    finalpath = j[:-1]+k
                    if k.rfind('/') == (len(k)-1):
                        oc.mkdir(finalpath)
                    else:
                        oc.put_file_contents(finalpath, str2)
            if type1=='file':
                return {'message': 'File created successfully'}
            else:
                return {'message': 'Folder created successfully'}
        else:
            return {'message': 'File or Folder already exists'}


    def modifyFile(self, filepath, filecontents):
        if self.fileExists(self.oc, filepath):
            oc = self.oc
            bool1, p = self.isFolder(filepath)
            if bool1:
                return {'message': 'Given Path is a Folder and not a file'}
            else:
                str1 = filecontents
                str2 = bytes(str1, 'UTF-8')
                oc.put_file_contents(p, str2)
                bool2, duplicateFileList = self.getDuplicateFileList(filepath)
                if bool2:
                    for iterations in duplicateFileList:
                        duplicateFilePath1 = iterations
                        oc.put_file_contents(duplicateFilePath1, str2)
                    return {'message': 'File modified successfully and duplicates updated'}
                else:
                    return {'message': 'File modified successfully'}
        else:
            return {'message': 'File or Folder does not exist'}

    def removeShare(self, username, userpasswrd, filepath):
        if self.fileExists(self.oc, filepath):
            oc = self.oc
            bool0, p = self.isFolder(filepath)
            bool1, duplicateFileList1, userList1 = self.checkDuplicateExist(filepath)
            duplicateFileList = self.column(duplicateFileList1, 0)
            userList = self.column(userList1, 0)
            if bool1:
                if username in userList:
                    for fileName in duplicateFileList:
                        if username in [i.get_share_with_displayname() for i in oc.get_shares(fileName)]:
                            shareId = userList1[userList.index(username)][1]
                            oc.delete_share(shareId)
                        if len(oc.get_shares(fileName)) == 0:
                            bool2, _ = self.isFolder(fileName)
                            oc.delete(fileName)
                            if bool2:
                                r = fileName[:-1].rfind('/')
                            else:
                                r = fileName.rfind('/')
                            dupDirectory = fileName[:r+1]
                            if len(oc.list(dupDirectory)) == 0:
                                oc.delete(dupDirectory)
                    ocu = self.ocUser(username, userpasswrd)
                    if bool0:
                        r = p[:-1].rfind('/')
                    else:
                        r = p.rfind('/')
                    ogDirectory = p[:r+1]
                    if len(ocu.list(ogDirectory)) == 0:
                        if ogDirectory != '/':
                            ocu.delete(ogDirectory)
                    return {'message': 'Share Removed Successfully'}
                else:
                    return {'message': 'File is not Shared to this user'}
            else:
                return {'message': 'File is not Shared'}
        else:
            return {'message': 'File or Folder does not exist'}

    def removeFileAdmin(self, filepath):
        if self.fileExists(self.oc, filepath):
            oc = self.oc
            list1 = self.dirPathList(filepath)[1]
            list0 = list1
            list1.reverse()
            list2 = []
            list3 = []
            ogDirectory = '/'
            if self.checkDuplicate(filepath):
                ogDirectory = filepath
            else:
                for i in list1:
                    if (not self.fileExists(self.oc,i)):
                        list2.append('/'+i[1:])
                    elif (not self.fileExists(self.oc,i)) and (not self.checkDuplicate(i)):
                        list2.append('/'+i[1:])
                    else:
                        ogDirectory = i
                        break
            list2.reverse()
            list4 = []
            [list4.append(i[len(ogDirectory)-1:]) for i in list2]
            list2 = list4
            list2.append(filepath[len(ogDirectory)-1:])
            if ogDirectory!="/":
                list4 = self.checkDuplicateExist(ogDirectory)
                bool0 = list4[0]
                list3 = self.column(list4[1],0)
                duplicatePath = self.duplicatePath(ogDirectory)
            list3.insert(0, ogDirectory)
            for j in list3:
                for k in list2:
                    finalpath = j[:-1]+k
                    if k.rfind('/') == (len(k)-1):
                        oc.delete(finalpath)
                    else:
                        oc.delete(finalpath)
            if bool0:
                if (duplicatePath != '/') and (len(oc.list(duplicatePath)) == 0):
                    oc.delete(duplicatePath)
                _, userData = self.getUserInfo(self.column(list4[2],0))
                for x in range(len(userData)):
                    ocu = self.ocUser(userData[x][0], userData[x][1])
                    for y in list0:
                        if (y != '/') and (len(ocu.list(y)) == 0):
                            ocu.delete(y)
            return {'message': 'File or Folder removed successfully'}
        else:
            return {'message': 'File or Folder does not exist'}

    def displayFiles(self, username, userpasswrd, filepath):
        ocu = self.ocUser(username,userpasswrd)
        fileList = [ [self.getTruePath(ocu,i),i.get_content_type(),i.get_last_modified()] for i in ocu.list(filepath) ]
        bool1 = 0
        ogDirectory = ''
        if filepath == '':
            bool1 = 1
            ogDirectory = ''
        else:
            bool1 = 0
            bool0, p = self.isFolder(filepath)
            if bool0:
                r = p[:-1].rfind('/')
            else:
                r = p.rfind('/')
            ogDirectory = p[:r+1]
        return bool1,ogDirectory,fileList

    def displayFilesAdmin(self, filepath):
        fileList = [ [self.getTruePath(self.oc,i),i.get_content_type(),i.get_last_modified()] for i in self.oc.list(filepath) ]
        fileList1 = []
        bool1 = 0
        ogDirectory = ''
        for elem in fileList:
            if (elem[0][:2] != '/.') and (elem[0][-11:] != 'Duplicates/'):
                fileList1.append(elem)
        fileList = fileList1
        if filepath == '':
            bool1 = 1
            ogDirectory = ''
        else:
            bool1 = 0
            bool0, p = self.isFolder(filepath)
            if bool0:
                r = p[:-1].rfind('/')
            else:
                r = p.rfind('/')
            ogDirectory = p[:r+1]
        return bool1,ogDirectory,fileList

    def request(self, returnData):
        x1 = returnData.encode('ascii')
        base64_bytes = base64.b64encode(x1)
        returnData = base64_bytes.decode('ascii')+'\n'
        fileData = self.oc.get_file_contents('/.file1.txt').decode('UTF-8')
        if returnData in fileData:
            return {'message':'File already Shared'}
        else:
            fileData = fileData + returnData
            self.oc.put_file_contents('/.file1.txt',bytes(fileData, 'UTF-8'))
            return {'message':'File request sent'}

    def updateRequest(self, returnData, updt):
        if updt == 'accept':
            base64_bytes = returnData.encode('ascii')
            message_bytes = base64.b64decode(base64_bytes)
            message = message_bytes.decode('ascii')
            returnList = message.split(',')
            _,userList = self.getUserInfo([returnList[0]])
            msg = self.shareFile(returnList[0],userList[0][1],returnList[1])
        else:
            msg = {'message':'File Share Rejected'}
        returnData = returnData +'\n'
        fileData = self.oc.get_file_contents('/.file1.txt').decode('UTF-8')
        fileData = fileData.replace(returnData,'')
        self.oc.put_file_contents('/.file1.txt',bytes(fileData, 'UTF-8'))
        return msg


    def readRequestList(self):
        returnList = []
        fileList = self.oc.get_file_contents('/.file1.txt').decode('UTF-8')
        if fileList != '':
            rList = fileList[:-1].split('\n')
            for i in rList:
                base64_bytes = i.encode('ascii')
                message_bytes = base64.b64decode(base64_bytes)
                message = message_bytes.decode('ascii')
                returnList.append(message.split(','))
        return returnList