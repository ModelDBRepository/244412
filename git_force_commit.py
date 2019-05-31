print("Updating git")
import git as gp
import os
repo = gp.repo.Repo('./')
if repo.is_dirty():
    os.system('git add -u')
    print('Insert a comment for this code (leave blank for default): ')
    comment = input('Insert a comment for this code (leave blank for default): ')
    print("Updating git")
    if len(comment) == 0:
        os.system('git commit -m "WIP commit"')
    else:
        os.system('git commit -m "%s"'%comment)
