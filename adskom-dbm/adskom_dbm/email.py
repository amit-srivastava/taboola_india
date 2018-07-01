# Download ALL attachments from GMail
# 1. Make sure you have IMAP enabled in your GMail settings.
#    https://support.google.com/mail/troubleshooter/1668960?hl=en
# 2. If you are using 2 step verification you may need an APP Password.
#    https://support.google.com/accounts/answer/185833
# 3. Reference information for GMail IMAP extension can be found here.
#    https://developers.google.com/gmail/imap_extensions


import email
import hashlib
import getpass
import imaplib
import os
from collections import defaultdict, Counter
import platform



class FetchEmail():
    
    connection = None
    imapSession = None
    error = None
    fileNameCounter = Counter()
    fileNameHashes = defaultdict(set)
    NewMsgIDs = set()
    ProcessedMsgIDs = set()

    def __init__(self, mail_server, username, password):
        self.imapSession = imaplib.IMAP4_SSL(mail_server)
        typ, accountDetails = self.imapSession.login(username, password)
    
        print(typ)
        print(accountDetails)
        if typ != 'OK':
            print('Not able to sign in!')
            raise
#         self.imapSession.select('[Gmail]/All Mail')
        self.imapSession.select(readonly=False) # so we can mark mails as read
        
    
    def close_connection(self):
        """
        Close the connection to the IMAP server
        """
        self.imapSession.close()
        self.imapSession.logout()
    
    def recover(self, resumeFile):
        if os.path.exists(resumeFile):
            print('Recovery file found resuming...')
            with open(resumeFile) as f:
                processedIds = f.read()
                for ProcessedId in processedIds.split(','):
                    self.ProcessedMsgIDs.add(ProcessedId)
        else:
            print('No Recovery file found.')
            open(resumeFile, 'a').close()
    
    
#     def GenerateMailMessages(userName, password, resumeFile):
    def GenerateMailMessages(self, resumeFile, subject, start_date, end_date):
        
#         print('(X-GM-RAW "has:attachment after:{} before:{} subject:{}")'.format(start_date, end_date, subject))
        
        typ, data = self.imapSession.search(None, '(X-GM-RAW "has:attachment after:{} before:{} subject:{}")'.format(start_date, end_date, subject))
        # typ, data = imapSession.search(None, 'ALL')
        if typ != 'OK':
            print('Error searching Inbox.')
            raise
    
        # Iterating over all emails
        for msgId in data[0].split():
            self.NewMsgIDs.add(msgId)
            typ, messageParts = self.imapSession.fetch(msgId, '(RFC822)')
            if typ != 'OK':
                print('Error fetching mail.')
                raise
            emailBody = messageParts[0][1]
            if msgId not in self.ProcessedMsgIDs:
#                 yield email.message_from_string(emailBody)
                yield email.message_from_bytes(emailBody)
                self.ProcessedMsgIDs.add(msgId)
                with open(resumeFile, "a") as resume:
                    resume.write('{id},'.format(id=msgId))
        
        self.close_connection()
#         self.imapSession.close()
#         self.imapSession.logout()
    
    
    def SaveAttachmentsFromMailMessage(self, message, directory):
        for part in message.walk():
            if part.get_content_maintype() == 'multipart':
                # print(part.as_string())
                continue
            if part.get('Content-Disposition') is None:
                # print(part.as_string())
                continue
            fileName = part.get_filename()
            if fileName is not None:
                fileName = ''.join(fileName.splitlines())
            if fileName:
                # print('Processing: {file}'.format(file=fileName))
                payload = part.get_payload(decode=True)
                if payload:
                    x_hash = hashlib.md5(payload).hexdigest()
    
                    if x_hash in self.fileNameHashes[fileName]:
                        print('\tSkipping duplicate file: {file}'.format(file=fileName))
                        continue
                    self.fileNameCounter[fileName] += 1
                    fileStr, fileExtension = os.path.splitext(fileName)
                    if self.fileNameCounter[fileName] > 1:
                        new_fileName = '{file}({suffix}){ext}'.format(suffix=self.fileNameCounter[fileName],
                                                                      file=fileStr, ext=fileExtension)
                        print('\tRenaming and storing: {file} to {new_file}'.format(file=fileName,
                                                                                    new_file=new_fileName))
                    else:
                        new_fileName = fileName
                        print('\tStoring: {file}'.format(file=fileName))
                    self.fileNameHashes[fileName].add(x_hash)
                    file_path = os.path.join(directory, new_fileName)
                    if os.path.exists(file_path):
                        print('\tExists in destination: {file}'.format(file=new_fileName))
                        continue
                    try:
                        with open(file_path, 'wb') as fp:
                            fp.write(payload)
                    except:
                        print('Could not store: {file} it has a shitty file name or path under {op_sys}.'.format(
                            file=file_path,
                            op_sys=platform.system()))
                else:
                    print('Attachment {file} was returned as type: {ftype} skipping...'.format(file=fileName,
                                                                                               ftype=type(payload)))
                    continue

