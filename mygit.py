"""
This is a simple git implementation that zips a folder of your choice 
and stores them in a repository folder so that whenever needed, it can be cloned back.

Beware that this project is not intended to be a fully featured 'new' git but is educational especially to give
inexperienced programmers an idea of how git works and how to make such projects in simple form



our database is a simple dictionary and its contents is written to a file using the json module
"""

import os
import sys
import json
import zipfile


# defining directories for mygit

BASE_DIR = os.path.expanduser('~/mygit/')
REPOS_DIR = os.path.expanduser('~/mygit/repos/')  # repositories directory

# check if the repositories folder already exits, if it doesn't, we create it
if not os.path.isdir(os.path.normpath(REPOS_DIR)):
    os.makedirs(os.path.normpath(REPOS_DIR))


# create empty dictionary as database and load contents of 'mygit.db' if it exits

db = {}

if os.path.isfile(os.path.normpath(os.path.expanduser(BASE_DIR+'mygit.db'))):
    db = dict(json.load(open(os.path.normpath(os.path.expanduser(BASE_DIR+'mygit.db')), 'r')))


def dump():
    """
    This function writes the contents of our dictionary 'db' to a file using json so that it can be read later
    """
    try:
        json.dump(db, open(os.path.normpath(os.path.expanduser(REPOS_DIR+'mygit.db')), 'w'), indent=4)
    except Exception as e:
        print("Could not save database: ", e)




def zipdir(path, repo, branch):
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
    with zipfile.ZipFile(os.path.normpath(REPOS_DIR+repo+f'/{branch}.zip'), 'w', zipfile.ZIP_DEFLATED) as ziph: 
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            # files whose names are in gitignore are not added 
            ziph.write(os.path.join(root, file_) for file_ in files if  file_ in gitignore)


def create_repo(name):
    """
    Creates a new repository.
     it basically adds the repository's name to the database and creates the directory for it.
    """
    if name not in list(db.keys()):
        db[name]=[]
        os.makedirs(os.path.normpath(REPOS_DIR+name))
    else:
        print("Repository {} already exists".format(name))
    dump()  # writes the db contents to a file


def commit(repo, branch):
    """
    creates a branch and saves the new contents of the folder to the repository folder
    """

    if repo in list(db.keys()):
        branches = db[repo]
        
        if not branch in branches:
            zipdir('.',repo, branch )
            branches.append( '{}.zip'.format(branch))
            db[repo] = branches
            dump()
        else:
            print('branch already exits')
    else:
        print(f"Repository {repo} does not exist. Please create it first")
    

def clone(repo, branch):
    """ clones the contents of a branch in a repository to the current directory 
        This is achieved by copying the zipfile related to the branch and expanding the contents to our directory
    """
    if repo in db.keys():
        if branch in db[repo]:
            try:
                with zipfile.ZipFile(os.path.normpath(REPOS_DIR + f'{repo}/{branch}.zip', 'r')) as ziph:
                    ziph.extractall(path=os.curdir)
            except Exception as e:
                print(f"Error cloing branch {branch} \n", e)
        else:
            print('Branch does not exist')
    else:
        print('Repository does not exist')


def list_repos():
    """
    Lists all the repositories there are so far
    """
    for key in db.keys():
        print(str(key), end="\t")


def list_branches(repo):
    """
    Lists all the branches in a repository
    """
    print("\t".join(db[repo]))


if __name__=='__main__':
    if len(sys.argv)>1:
        if sys.argv[1] == "clone" and not 'commit' in sys.argv and len(sys.argv)==3:
            repo = sys.argv[2]
            branch = sys.argv[3]
            print(f"Cloning {branch} from repository {repo}")
            clone(repo, branch)

        elif sys.argv[1] == "commit" and not "clone" in sys.argv:
            repo = sys.argv[2]
            branch = sys.argv[3]
            print(f'Commiting directory as branch {branch} to repository {repo}')
            commit(repo, branch)

        if sys.argv[1]=='list' and len(sys.argv)==2:
            list_repos()

        elif sys.argv[1]=='list' and not len(sys.argv)==2:
            list_branches(sys.argv[2])
            
        if sys.argv[1]=='create' and len(sys.argv)==3:
            create_repo(sys.argv[2])
        
        else:
            print(
                """ Your command was not understood.\n Try commands such as\n
                    mygit clone repository_name branch_name\n
                    mygit create repository_name \n
                    mygit commit repository_name branch_name\n
                    """
                )
