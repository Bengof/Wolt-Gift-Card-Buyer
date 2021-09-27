import datetime
from time import sleep
import configparser
import os

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

now = datetime.datetime.now()


POSSIBLE_GIFT_CARDS = [20, 25, 30, 35, 40, 45, 60, 70, 80, 100]


def get_identifiers():
    # credentials for login in the format:
    # username,password,company
    f = open("login_details.txt", "r", encoding='utf-8')
    contents = f.read()
    contents = contents.split(",")
    f.close()
    return contents[0], contents[1], contents[2]


def get_firefox_profile_path():
    mozilla_profile = os.path.join(os.getenv('APPDATA'), r'Mozilla\Firefox')
    mozilla_profile_ini = os.path.join(mozilla_profile, r'profiles.ini')
    profile = configparser.ConfigParser()
    profile.read(mozilla_profile_ini)
    return(os.path.normpath(os.path.join(mozilla_profile, profile.get(
        'Profile0', 'Path'))))


def run_driver():
    profile = webdriver.FirefoxProfile(get_firefox_profile_path())

    profile.set_preference("dom.webdriver.enabled", False)
    profile.set_preference("dom.webdriver.enabled", False)
    profile.set_preference('useAutomationExtension', False)
    profile.update_preferences()
    desired = DesiredCapabilities.FIREFOX
    driver = webdriver.Firefox(firefox_profile=profile,
                               desired_capabilities=desired)
    return driver

def get_budget(driver):
    username, password, company = get_identifiers()
    driver.get('https://www.mysodexo.co.il/new_my/new_my_budget.aspx')
    name_elem = driver.find_element_by_css_selector('#txtUsr')
    name_elem.send_keys(username)

    name_elem = driver.find_element_by_css_selector('#txtPas')
    name_elem.send_keys(password)

    name_elem = driver.find_element_by_css_selector('#txtCmp')
    name_elem.send_keys(company)
    driver.find_element_by_css_selector('#btnLogin').click()

    driver.get('https://www.mysodexo.co.il/new_my/new_my_budget.aspx')
    budget_obj = driver.find_element_by_css_selector("table.fixed-table:nth-child(3) > tbody:nth-child(1) > tr:nth-child(3) > td:nth-child(4) > b:nth-child(1)")
    return int(budget_obj.text)


def calc_max_gift_card(budget):
    return max([price for price in POSSIBLE_GIFT_CARDS if price <= budget])


def buy_gift_card(price, driver):
    index = POSSIBLE_GIFT_CARDS.index(price) + 1
    driver.get("https://wolt.com/en/isr/ashdod/venue/woltilgiftcards")
    sleep(2)

    elements = driver.find_elements_by_xpath("//div[contains(@class,"
                                             "'MenuItem-module__itemContainer')]")
    elements[index].click()
    sleep(2)
    # Buy relevant gift card
    driver.find_element_by_xpath("//div[contains(@class, "
                                  "'ProductViewFooter__SubmitButtonContent')]").click()
    sleep(2)
    # Checkout
    driver.find_element_by_xpath("//div[contains(@data-test-id, "
                                 "'CheckoutButton')]").click()
    sleep(2)

    # Verify payment with cibus
    driver.find_element_by_partial_link_text("cibus").click()


def main():
    driver = run_driver()
    total_budget = get_budget(driver)
    max_card_budget = calc_max_gift_card(total_budget)
    buy_gift_card(max_card_budget, driver)
    sleep(2)
    driver.close()


if __name__ == '__main__':
    main()
    # print(get_firefox_profile_path())