from main_zhilian import *

lagou_url = 'https://www.lagou.com/'

def lagou_search_key(keyword, main_browser, wait, url=lagou_url):
    print("正在搜索：" + keyword)
    main_browser.get(url)
    try:
        btn = wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, '深圳站'))
        )
        btn.click()
    except Exception:
        pass

    try:
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#search_input'))
        )
        btn_search = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#search_button'))
        )
        input.send_keys(keyword)
        time.sleep(2)
        btn_search.click()
        # handle = main_browser.current_window_handle
        # handles = main_browser.window_handles
        # if len(handles) > 1:
        #     for h in handles:
        #         if h != handle:
        #             main_browser.switch_to_window(h)
        #             time.sleep(2)
        #             return main_browser.page_source
        # else:
        #     return main_browser.page_source
        time.sleep(2)
        return main_browser.page_source
    except TimeoutException:
        lagou_search_key(keyword, main_browser, wait)

def lagou_csv_write(csv_name, headers, html, writeheader = True):
    if writeheader:
        write_csv_headers(csv_name, headers)
    others = lagou_parse_page_shezhao(html)
    write_csv_rows(csv_name, headers, others)

def lagou_parse_page_shezhao(html):
    soup = BeautifulSoup(html, "lxml")
    message_dict = []
    li_list = soup.select('ul.item_con_list > li.con_list_item')
    # print(len(li_list))
    for li in li_list:
        messdict = {}
        position_link = ""
        position_name = ""
        position_local = ""
        format_time = ""
        money = ""
        base_desc = ""
        company_name = ""
        company_link = ""
        industry = ""
        p_top = li.select('div.list_item_top > div.position > div.p_top')
        if len(p_top)>0:
            p_top_a = p_top[0].select('a.position_link')
            if len(p_top_a) > 0:
                position_link = p_top_a[0].attrs['href']
                if len(p_top_a[0].select('h3')) > 0:
                    position_name = p_top_a[0].select('h3')[0].get_text()
                if len(p_top_a[0].select('span.add'))>0:
                    position_local = p_top_a[0].select('span.add')[0].get_text()
            span_format_time = p_top[0].select('span.format-time')
            if len(span_format_time)>0:
                format_time = span_format_time[0].get_text()
        p_bot = li.select('div.list_item_top > div.position > div.p_bot')
        if len(p_bot) > 0:
            base_desc_re = p_bot[0].get_text().replace('\n', '')
            base_desc = base_desc_re.split('k')[-1].replace(' ', '')
            span_money = p_bot[0].select('div > span.money')
            if len(span_money) > 0:
                money = span_money[0].get_text().replace('\n', '')
        company_name_tag = li.select('div.list_item_top > div.company > div.company_name')
        if len(company_name_tag)>0:
            company_name = company_name_tag[0].select('a')[0].get_text()
            company_link = company_name_tag[0].select('a')[0].attrs["href"]
        industry_tag = li.select('div.list_item_top > div.company > div.industry')
        if len(industry_tag)>0:
            industry = industry_tag[0].get_text().replace('\n', '').replace(' ', '')
        messdict['发布时间'] = format_time
        messdict['职位链接'] = position_link
        messdict['职位'] = position_name
        messdict['职位位置'] = position_local
        messdict['薪资'] = money
        messdict['基本要求'] = base_desc
        messdict['公司'] = company_name
        messdict['公司规模'] = industry
        messdict['公司链接'] = company_link
        message_dict.append(messdict)
    return message_dict

def lagou_next_page(main_browser, wait, max_page=100):
    try:
        page_click = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.pager_next '))
            )
        page_click.click()
        pager_is_current = main_browser.find_element_by_css_selector('.pager_is_current')
        current_page = int(pager_is_current.text)
        if current_page > max_page:
            return None
        return main_browser.page_source
    except TimeoutException:
        return None

def main():
    # filename = input("请输入搜索关键词：\n").replace(' ', '_')
    # filename = "java"
    # max_page = 4
    filename = input("请输入搜索关键词：\n").replace(' ', '_')
    max_page = int(input('请输入存储页数：\n'))
    b, w = create_browser()
    html = lagou_search_key(filename, b, w)
    # lagou_parse_page_shezhao(html)
    csv_name = filename + '.csv'
    headers = ['发布时间','职位链接', '职位', '职位位置','薪资', '基本要求', '公司', '公司规模', '公司链接']
    lagou_csv_write(csv_name, headers, html)
    while True:
        time.sleep(2)
        html = lagou_next_page(b, w, max_page)
        if not html:
            break
        else:
            lagou_csv_write(csv_name, headers, html, writeheader = False)
    b.quit()

if __name__=="__main__":
    main()