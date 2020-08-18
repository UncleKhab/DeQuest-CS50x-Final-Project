---CS50x FINAL PROJECT---

-- Made By: Cojocaru Stefan-Alexandru

-- Project Name: DeQuest

-- Technologies: HTLM / CSS / PYTHON(FLASK) / JAVASCRIPT / SQL

-------------------------------------------------------------

--DeQuest is a web application which allows you to create a single-choice quiz or take already made quizzes available in the quiz-list.

--The interface is simple and intuitive to use, making it very easy to get started.

How to use this web app:
    + When you first access the page you'll be prompted with a login and a register button,
        press one or the other and you'll be show a drowdown form asking you for your credentials.
    + After you login/register, you'll be taken to the homepage where you'll see some cards with
        features for this app.
    + In the navigation bar (burger-menu on mobile) you'll see the following (PROFILE / CREATE / QUIZ / LEADERBOARDS)


--------The Profile Option shows you: - a list with quizzes you created so far(allowing you to remove any of them from the database)
                                  - a list of quizzes you completed and chose to be displayed on your profile.


--------The Create Option prompts you with a form asking for details about the quiz(Title, Description, Subject, Difficulty)

            The Create button is disabled until you completed all the fields.

            After you press Create, a button for adding question will be shown,when pressed a dropdown form will be shown

            Add your question in the question filed and complete the 4 required fileds for answers

            The Add button is disabled until you completed all the required fields.
                If you try to press submit without choosing a correct answer, you'll be shown an alert asking you to select one answer.

            Once you add the first question, you'll see a list of questions under the Add a Question button and a "Done Button"
                You can add as many questions as you want, once you press Done, the quiz will be saved into the database and you can view it
                on your profile.


--------Quiz Option allows you to take a quiz of your choice, this is a list of all the quizzes in the database ordered(desc) by the amount of times
        it was taken.
        Once you press Take Quiz, the quiz will be loaded and available for you to take
            When you submit, the results will appear on the screen (you need at least 50% to pass)
            If you pass you'll be able to add this quiz to your profile (under completed quizzes)
            If you fail, you'll be able to retry the quiz

--------The Leaderboards Option allows you to see the leaderboards for Quiz Makers and Quiz Takers


How does it work?

--------Routing
            Each Route checks if the user is authenticated and gives access to all the options described above

--------Sessions
            The webapp uses sessions to confirm that the user is registered passing the info into flask sessions and opening a single session
            for each user

--------Database
            The database stores
                User Credentials(passwords is hashed using werkzeug library)
                Quiz Info(Title, Description, Subject, Difficulty, Times Taken)
                Questions/Answers
                    They are linked to the quiz using the quiz.id
                    Answers are linked to questions using the questions.id
                Profile
                    Stores the quiz id's that the user has taken as well as the score for any give quiz

Possible Improvements:
    - Adding a Search Bar for quizzes
    - Allowing user to see other users profiles
    - Generating custom links for each quiz
    - Allowing user to modify and update a quiz
    - Creating a Categories option
    - Multiple ways of sorting the quiz list\


I hope you have a great day!

This Was CS50!

Kind Regards , Stefan Cojocaru!
