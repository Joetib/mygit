"""
This is a simple git implementation that zips a folder of your choice 
and stores them in a repository folder so that whenever needed, it can be cloned back.

Beware that this project is not intended to be a fully featured 'new' git but is educational especially to give
inexperienced programmers an idea of how git works and how to make such projects in simple form



our database is a simple dictionary and its contents is written to a file using the json module
"""

import os, sys, json, zipfile, cmd

# defining directories for mygit
class Mygit(cmd.Cmd):
    
    intro = """
    Welcome to the mygit shell. Type help or ? to list commands.
    Type 'quit' to exit """

    prompt = '(mygit) '
    BASE_DIR = os.path.expanduser('~/mygit/')
    REPOS_DIR = os.path.expanduser('~/mygit/repos/')  # repositories directory
    file = None

    # check if the repositories folder already exits, if it doesn't, we create it
    if not os.path.isdir(os.path.normpath(REPOS_DIR)):
            os.makedirs(os.path.normpath(REPOS_DIR))
        
    # create empty dictionary as database and load contents of 'mygit.db' if it exits
    db = {}
    if os.path.isfile(os.path.normpath(os.path.expanduser(BASE_DIR+'mygit.json'))):
        db = dict(json.load(open(os.path.normpath(os.path.expanduser(REPOS_DIR+'mygit.json')), 'r')).readlines())

    def default(self, arg):
        print(
                    """ Your command was not understood.\n Try commands such as\n
                        (mygit) clone repository_name branch_name\n
                        (mygit) create repository_name \n
                        (mygit) listr (list repos)
                        (mygit) listb (list branches)
                        (mygit) commit repository_name branch_name\n
                        """
                    )
    def do_quit(self, arg):
        'Stop recording, close end mygit session, and exit: BYE'
        print('Thank you for using Mygit')
        self.close()
        return True
    
    def do_record(self, arg):
        'Save future commands to filename: RECORD rose.cmd'
        self.file = open(arg, 'w')

    def do_playback(self, arg):
        'Playback commands from a file: PLAYBACK rose.cmd'
        self.close()
        with open(arg) as f:
            self.cmdqueue.extend(f.read().splitlines())
    
    def close(self):
        if self.file:
            self.file.close()
            self.file = None

    def precmd(self, line):
        line = line.lower()
        if self.file and 'playback' not in line:
            print(line, file=self.file)
        return line

    def dump(self):
        """
        This function writes the contents of our dictionary 'db' to a file using json so that it can be read later
        """
        try:
            json.dump(self.db, open(os.path.normpath(os.path.expanduser(self.REPOS_DIR+'mygit.json')), 'w'), indent=4)
        except Exception as e:
            print("Could not save database: ", e)

    def zipdir(self, path, repo, branch):
        """
        creates a zipfile containing the contents of a folder and saves it to the folder specified
        in the branch argument.
        """


        # we represent the contents of git ignore to a list. Our git ignore does not check regular expressions but exact names
        gitignore = []
        if os.path.isfile('gitignore.txt'):
            with open("gitignore.txt", 'r') as f:
                gitignore = f.readlines().strip(" ")

        # the folder must exist for this to work
        with zipfile.ZipFile(os.path.normpath(self.REPOS_DIR+repo+f'/{branch}.zip'), 'w', zipfile.ZIP_DEFLATED) as ziph: 
            # ziph is zipfile handle
            for root, dirs, files in os.walk(path):
                # files whose names are in gitignore are not added 
                for file_ in files:
                     if  not file_ in gitignore:
                         ziph.write(os.path.join(root, file_))

    def do_create(self, name):
        """
        Creates a new repository.
        it basically adds the repository's name to the database and creates the directory for it.
        """
        if name not in list(self.db.keys()):
            self.db[name]=[]
            os.makedirs(os.path.normpath(self.REPOS_DIR+name))
        else:
            print("Repository {} already exists".format(name))
        self.dump()  # writes the db contents to a file

    def do_commit(self, arg):
        """
        creates a branch and saves the new contents of the folder to the repository folder
        """
        self.commit(*parse(arg))

    def commit(self, repo, branch):
        if repo in self.db.keys():
            branches = self.db[repo]
            if not branch in branches:
                self.zipdir(os.curdir, repo, branch)
                branches.append( '{}.zip'.format(branch))
                self.db[repo] = branches
                self.dump()
                print(f'Committed directory as branch {branch} to repository {repo}')
            else:
                print('branch already exits')
        else:
            print(f"Repository {repo} does not exist. Please create it first")
        

    def do_clone(self, repo, branch):
        """ clones the contents of a branch in a repository to the current directory 
            This is achieved by copying the zipfile related to the branch and expanding the contents to our directory
        """
        print(f"Cloning {branch} from repository {repo}")

        if repo in self.db.keys():
            if branch in self.db[repo]:
                try:
                    with zipfile.ZipFile(os.path.normpath(self.REPOS_DIR + f'{repo}/{branch}.zip', 'r')) as ziph:
                        ziph.extractall(path=os.curdir)
                except Exception as e:
                    print(f"Error cloing branch {branch} \n", e)
            else:
                print('Branch does not exist')
        else:
            print('Repository does not exist')

    def do_listr(self, arg):
        """
        Lists all the repositories there are so far
        """
        print(self.db)
        for key in self.db.keys():
            print(str(key), end="\t")

    def do_listb(self, repo):
        """
        Lists all the branches in a repository
        """
        print(self.db)
        for branch in self.db[repo]:
            print(branch, end='\t')

def parse(arg):
    """
    Split arguments
    """
    return tuple(arg.split())

if __name__=='__main__':
    mygit = Mygit()
    mygit.cmdloop()
