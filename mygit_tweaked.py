"""
This is a simple git implementation that zips a folder of your choice 
and stores them in a repository folder so that whenever needed, it can be cloned back.

Beware that this project is not intended to be a fully featured 'new' git but is educational especially to give
inexperienced programmers an idea of how git works and how to make such projects in simple form



our database is a simple dictionary and its contents is written to a file using the json module
"""

import os, json, zipfile, cmd

# defining directories for mygit
class Mygit(cmd.Cmd):
    
    intro = """
    Welcome to the mygit shell. Type help or ? to list commands.
    Type 'quit' to exit """
    
    prompt = '\n(mygit) '
    BASE_DIR = os.path.expanduser('~/AppData/Local/mygit/')
    REPOS_DIR = os.path.expanduser('~/mygit/repos/')  # repositories directory
    file = None

    # check if the repositories folder already exits, if it doesn't, we create it
    base_dir_exists = os.path.isdir(os.path.normpath(BASE_DIR))
    repo_dir_exists = os.path.isdir(os.path.normpath(REPOS_DIR))
    if not base_dir_exists:
        os.makedirs(os.path.normpath(BASE_DIR))
    if not repo_dir_exists:
        os.makedirs(os.path.normpath(REPOS_DIR))
            
        
    # create empty dictionary as database and load contents of 'mygit.db' if it exits
    db = {}
    if os.path.isfile(os.path.normpath(os.path.expanduser(REPOS_DIR+'mygit.db'))):
        db = json.load(open(os.path.normpath(os.path.expanduser(REPOS_DIR+'mygit.db')), 'r')) 
        
    def default(self, arg):
        print(
                    """ Your command was not understood.\nTry commands such as:\n
                    (mygit) clone [repository_name] [branch_name]
                    (mygit) create [repository_name]
                    (mygit) listr -> (list repos)
                    (mygit) listb [repository_name] -> (list branches in [repository_name])
                    (mygit) commit [repository_name] [branch_name]
                    Type help for more info
                    Type quit to exit
                    """
                    )
    def do_quit(self, arg):
        'Stop recording, close end mygit session, and exit: BYE'
        print('Thank you for using Mygit\n')
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
    
    def do_clear(self, arg):
        'Clear screen'
        print('\n'*500)

    def dump(self):
        """
        This function writes the contents of our dictionary 'db'
        to a file using json so that it can be read later
        """
        try:
            json.dump(self.db, open(os.path.normpath(os.path.expanduser(self.REPOS_DIR+'mygit.db')), 'w'), indent=4)
        except Exception as e:
            print("Could not save database: ", e)

    def zipdir(self, path, repo, branch):
        """
        creates a zipfile containing the contents of a 
        folder and saves it to the folder specified
        in the branch argument.
        """

        # we represent the contents of git ignore to a list. Our git ignore does not check regular expressions but exact names
        gitignore = []
        gitignore_file = os.path.normpath(self.REPOS_DIR+repo+'gitignore.txt')
        if os.path.isfile(gitignore_file):
            with open("gitignore.txt", 'r') as f:
                reader = f.readlines()
                for line in reader:
                    gitignore.append(line.strip())

        # the folder must exist for this to work
        zipfile_ = os.path.normpath(self.BASE_DIR+f'/{branch}.zip')
        print(zipfile_)
        print(list(os.walk(path)))
        with zipfile.ZipFile(zipfile_, 'w', zipfile.ZIP_DEFLATED) as ziph: 
            # ziph is zipfile handle
            for root, dirs, files in os.walk(path):
                # files whose names are in gitignore are not added 
                for name in files:
                     if  not name in gitignore:
                         ziph.write(os.path.normpath(os.path.join(root, name)), arcname=name)
                         
                        
    def do_create(self, name):
        """
        Creates a new repository.
        It basically adds the repository's name
        to the database and creates the directory for it.
        SYNTAX: (mygit) create [repository_name]
        """
        if name not in list(self.db.keys()):
            self.db[name]=[]
            os.makedirs(os.path.normpath(self.REPOS_DIR+name))
        else:
            print("Repository {} already exists".format(name))
        self.dump()  # writes the db contents to a file
        print(f"Created repository {name}")

    def do_commit(self, arg):
        """
        creates a branch and saves the new 
        contents of the folder to the repository folder
        SYNTAX: (mygit) commit [repository_name] [branch_name]
        """
        self.commit(*parse(arg))
 
    def commit(self, repo, branch):
        folder_name = os.path.normpath(self.REPOS_DIR+repo)
        if repo in self.db.keys():
            branches = self.db[repo]
            if not branch in branches:
                self.zipdir(folder_name, repo, branch)
                branches.append( '{}.zip'.format(branch))
                self.db[repo] = branches
                self.dump()
                print(f'Committed directory as branch {branch} to repository {repo}')
            else:
                print('branch already exits')
        else:
            print(f"Repository {repo} does not exist. Please create it first")
    
    def do_delete(self, arg):
        """
        Deletes a branch from a specified repository
        SYNTAX: (mygit) delete [repository_name] [branch_name]
        """
        self.delete(*parse(arg))
    
    def delete(self, repo, branch):
        try:
            branch_name = branch+'.zip'
            branches = self.db[repo]
            os.remove(os.path.normpath(f'{self.BASE_DIR}/{branch_name}'))
            branches.remove(branch_name)
            self.db[repo] = branches
            self.dump()
            print(f"Deleted branch {branch} from repository {repo}")
        except Exception as e:
            print(f"Error deleting branch \n", e)
            
    def do_clone(self, arg):
        """
        clones the contents of a branch in a 
        repository to the current directory 
        This is achieved by copying the zipfile related 
        to the branch and expanding the contents to our directory
        SYNTAX: (mygit) clone [repository_name] [branch_name]
        """
        self.clone(*parse(arg))

    def clone(self, repo, branch):
        print(f"Cloning {branch} from repository {repo} into current directory")
        if repo in self.db.keys():
            if branch+'.zip' in self.db[repo]:
                try:
                    with zipfile.ZipFile(os.path.normpath(self.BASE_DIR + f'/{branch}.zip'), 'r') as ziph:
                        ziph.extractall(path=os.curdir)
                except Exception as e:
                    print(f"Error cloning branch {branch} \n", e)
            else:
                print('Branch does not exist')
        else:
            print('Repository does not exist')

    def do_listr(self, arg):
        """
        Lists all the repositories there are so far
        SYNTAX: (mygit) listr
        """
        for key in self.db.keys():
            print(str(key), end="\t")

    def do_listb(self, repo):
        """
        Lists all the branches in a repository
        SYNTAX: (mygit) listb [repository_name]
        """
        for branch in self.db[repo]:
            print(branch, end='\t\t')

def parse(arg):
    """
    Split arguments
    """
    return tuple(arg.split())

if __name__=='__main__':
    Mygit().cmdloop()
