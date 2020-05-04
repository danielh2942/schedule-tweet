login_button = 'a.Button.Button--primary.block.txt-size--18.txt-center'


def load(browser):
    browser.load('https://tweetdeck.twitter.com/')


def go_to_login_page(browser):
    browser.click(login_button)
