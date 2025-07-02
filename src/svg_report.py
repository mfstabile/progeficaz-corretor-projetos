import base64
import db.db_conn as db
import os

class RepoReport:
    def __init__(self, git_username, repository_name, project_name):
        self.hspace = 5
        self.taglist = []
        self.code = ''
        self.height = 20
        self.width=0

        self.git_username = git_username
        self.repository_name = repository_name
        self.project_name = project_name

        self.db_update()


    def db_update(self):
        self.taglist = []

        reg = db.get_repo_release_status(self.git_username, self.repository_name, self.project_name)
        if len(reg) == 0:
            self.addtag('Invalid link', 'NOT_FOUND')

        for release in reg:
            version = release[0]
            test_status = release[1]
            self.addtag(version, test_status)


    # def save(self):
    #     self.compile()

    #     SVG_FOLDER = os.environ.get('SVG_FOLDER')
        
    #     svg_file = '{}_{}.svg'.format(self.git_username, self.repository_name)
    #     svg_file = os.path.join(SVG_FOLDER, svg_file)

    #     with open(svg_file, 'w') as arq:
    #         arq.write(self.code)
    #         arq.close()


    def compile(self):
        tagcode = ''
        xpos = 0

        for tag in self.taglist:
            tagcode += tag.compile(xpos)
            xpos = xpos + tag.width + self.hspace

        self.width = xpos - self.hspace

        self.code = '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">\n' + \
                    '<linearGradient id="a" x2="0" y2="100%">\n' + \
                    '    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>\n' + \
                    '    <stop offset="1" stop-opacity=".1"/>\n' + \
                    '</linearGradient>\n\n'

        self.code += tagcode

        self.addscreenshot()

        self.code += '</svg>'

        return(self.code)
    

    def addscreenshot(self):
        #check if file exists

        SVG_FOLDER = os.environ.get('SVG_FOLDER')
        screenshot_file = 'ss_{}_{}.png'.format(self.git_username, self.repository_name)
        screenshot_file = os.path.join(SVG_FOLDER, screenshot_file)
        print(screenshot_file)

        if os.path.isfile(screenshot_file):
            with open(screenshot_file, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
                data_uri = f"data:image/png;base64,{encoded_string}"
                width = 120
                height = 70
                factor = 4
                self.code += '<image width="{}" height="{}" x="80" y="30" href="{}"/>\n'.format(width*factor, height*factor, data_uri)
        else:
            self.code += '<text x="10" y="50" fill="#010101">Screenshot not found</text>\n'
            print('File not found')


    def addtag(self, version, teststatus):
        tagreport = TagReport(version, teststatus, self.height)
        self.taglist.append(tagreport)
        

class TagReport():
    def __init__(self, version, teststatus, height):
        
        self.versionwidth = len(version) * 6 + 20
        self.versiontextoffset = 10

        self.testwidth = 40
        self.testtextoffset = 18

        self.width = self.versionwidth + self.testwidth
        self.height = height

        self.code = ''
        self.version = version
        self.setteststatus(teststatus)


    def setteststatus(self, teststatus):
        if teststatus == 'ERROR':
            self.testcolor = '#ff4d4d'
            self.teststatus = 'Error'
        elif teststatus == 'PASS':
            self.testcolor = '#00b300'
            self.teststatus = 'Pass'
        elif teststatus == 'FAILED':
            self.testcolor = '#ff9933'
            self.teststatus = 'Fail'
        elif teststatus == 'NOT_FOUND':
            self.testcolor = '#c266ff'
            self.teststatus = 'To do'
        else:
            raise ValueError('Invalid test status: {}'.format(teststatus))


    def compile(self, x):
        xtest = x + self.versionwidth

        xtextversion = x + self.versiontextoffset
        xtexttest = x + self.versionwidth + self.testtextoffset

        self.code = '<rect rx="3" x="{}" y="0" width="{}" height="{}" fill="#595959"/>\n'.format(x, self.width, self.height) + \
                    '<rect rx="3" x="{}" y="0" width="{}" height="{}" fill="{}"/>\n'.format(xtest, self.testwidth, self.height, self.testcolor) + \
                    '<g fill="#fff" text-anchor="left" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">\n' + \
                    '    <text x="{}" y="15" fill="#010101" fill-opacity=".3">{}</text><text x="{}" y="14">{}</text>\n'.format(xtextversion, self.version, xtextversion, self.version) + \
                    '</g>\n' + \
                    '<g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">\n' + \
                    '    <text x="{}" y="15" fill="#010101" fill-opacity=".3">{}</text><text x="{}" y="14">{}</text>\n'.format(xtexttest, self.teststatus, xtexttest, self.teststatus) + \
                    '</g>\n'
        return(self.code)