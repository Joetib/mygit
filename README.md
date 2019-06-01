### MyGit
This is a simple implementation of git in python.

It has no dependencies other than the python standard library.

In its implementation, It zips the directory you want to commit and saves the zip file to a repository directory which is set to 
  ```C:/user/username/mygit/```
  
Every commit is saved and called a branch in this implementation ```sorry if my terminology serves wrong here```

You can create new repository using
  ```mygit create repositoryname```
  
To create a branch and make a commit, use
  ```mygit commit repositoryname branchname```

You can view all created repositories using
  ```mygit list```

You can list branches in a repository using 
  ```mygit list repositoryname```

Later you can get your code back by cloning it using 
  ```mygit clone repositoryname branchname ```
