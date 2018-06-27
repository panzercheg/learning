commit_log_notify is used for QA notifications about the developers commits from their teams.
How To: 
    * first you must aplly that command on you build-machine "git config --global grep.extendedRegexp true". Need for regexp from "git log"
    * I`m use next command - git log --pretty=format:"%an, %ai : %s https://w1-git.mail.msk/t1/aw/commit/%H" --author="git author|git author|git author" --since="yesterday 07:00" --until="today 07:00" - show author of commit, commit date, summary of commit and link to gitlab-commit ( helpful for QA) from one day ( from yesterday 07:00 to today 07:00)
    * you can change command - to another git log or something else
    * finaly we send e-mail to QA ( format - qa@youdomen.com) - subject e-mail: "Daily commits dd-mm-xxxx" and body e-mail: oneline output from git command above

git_log_by_author/commit_log_notify.py /path/to/repo ( like "python -u it_log_by_author/commit_log_notify.py /path/to/repo" )

