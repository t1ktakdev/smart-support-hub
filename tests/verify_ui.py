"""Real Chromium UI checks and screen captures for Smart Support Hub.
Run: python tests/verify_ui.py (requires selenium and local HTTP server on 8765).
"""
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select,WebDriverWait
import json,base64,time
ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'evidence'
EVIDENCE.mkdir(exist_ok=True)
BASE='http://127.0.0.1:8765/'
results=[]
def check(name, fn):
    try:
        outcome=fn()
        assert outcome is not False, 'returned false'
        results.append({'test':name,'status':'PASS','details':''})
        print('PASS',name)
    except Exception as exc:
        results.append({'test':name,'status':'FAIL','details':str(exc)[:350]})
        print('FAIL',name, str(exc)[:200])
def count(driver,sel):return len(driver.find_elements(By.CSS_SELECTOR,sel))
def assert_eq(actual,expected):
    assert actual==expected,(actual,expected)
def text(driver,sel):return driver.find_element(By.CSS_SELECTOR,sel).text
def click(driver,sel):driver.find_element(By.CSS_SELECTOR,sel).click()
def fill(driver,sel,value):
    field=driver.find_element(By.CSS_SELECTOR,sel);field.clear();field.send_keys(value)
def go(driver,page):
    driver.get(BASE+page)
    WebDriverWait(driver,8).until(lambda d:d.execute_script('return document.readyState')=='complete')
    time.sleep(.12)
def screenshot(driver,name):
    driver.save_screenshot(str(EVIDENCE/name))
def no_horizontal_overflow(driver):
    return driver.execute_script('return document.documentElement.scrollWidth <= document.documentElement.clientWidth')
opts=webdriver.ChromeOptions()
opts.add_argument('--headless=new')
opts.add_argument('--no-first-run')
opts.add_argument('--disable-gpu')
opts.add_argument('--window-size=1366,900')
opts.set_capability('goog:loggingPrefs',{'browser':'ALL'})
driver=webdriver.Chrome(options=opts)
try:
    driver.set_window_size(1366,900)
    go(driver,'index.html')
    driver.execute_script('localStorage.clear();location.reload()')
    time.sleep(.25)
    check('Dashboard renders correct open incident count',lambda:assert_eq(text(driver,'#kpiIncidents'),'3'))
    check('Five navigation sections',lambda:assert_eq(count(driver,'nav[aria-label="Основная навигация"] a'),5))
    check('Initial SLA success 67%',lambda:assert_eq(text(driver,'#kpiSla'),'67%'))
    check('Chart.js is locally loaded and charts initialized',lambda:assert_eq(driver.execute_script("return typeof Chart==='function' && !!document.querySelector('#priorityChart') && !!document.querySelector('#maintenanceChart')"),True))
    screenshot(driver,'01-dashboard-1366.png')
    go(driver,'incidents.html')
    check('List is visible before create form',lambda:assert_eq(driver.find_element(By.CSS_SELECTOR,'#new-incident').get_attribute('open'),None))
    click(driver,'a[href="#new-incident"]')
    check('New incident dialog opens',lambda:assert_eq(driver.find_element(By.CSS_SELECTOR,'#new-incident').get_attribute('open'),'true'))
    click(driver,'#incidentForm button[type=submit]')
    check('Empty incident title is rejected',lambda:assert_eq(text(driver,'#incidentError'),'Введите название обращения.'))
    fill(driver,'#incidentTitle','Тестовое обращение: высокая нагрузка')
    check('Inline error clears on typing',lambda:assert_eq(text(driver,'#incidentError'),''))
    Select(driver.find_element(By.CSS_SELECTOR,'#incidentForm select[name=priority]')).select_by_value('high')
    click(driver,'#incidentForm button[type=submit]')
    check('Successful create closes the dialog',lambda:assert_eq(driver.find_element(By.CSS_SELECTOR,'#new-incident').get_attribute('open'),None))
    check('High priority incident appears',lambda:(assert_eq(count(driver,'#incidentTable tr'),7),assert_eq('Высокий' in text(driver,'#incidentTable tr:first-child'),True)))
    screenshot(driver,'03-incidents-1366.png')
    Select(driver.find_element(By.CSS_SELECTOR,'#statusFilter')).select_by_value('resolved')
    check('Status filtering works',lambda:assert_eq(count(driver,'#incidentTable tr'),3))
    Select(driver.find_element(By.CSS_SELECTOR,'#statusFilter')).select_by_value('all')
    fill(driver,'#incidentSearch','Тестовое обращение')
    check('Search filtering works',lambda:assert_eq(count(driver,'#incidentTable tr'),1))
    click(driver,'#incidentTable button[data-action=resolve]')
    check('Incident can be resolved',lambda:assert_eq(driver.execute_script('return getData("incidents").find(x=>x.title.includes("высокая нагрузка")).status'),'resolved'))
    go(driver,'index.html')
    check('Dashboard reflects resolved incident',lambda:assert_eq(text(driver,'#kpiIncidents'),'3'))
    go(driver,'incidents.html')
    check('Created incident remains after page reload',lambda:assert_eq(count(driver,'#incidentTable tr'),7))
    go(driver,'maintenance.html')
    click(driver,'a[href="#new-request"]')
    fill(driver,'#requestForm input[name=title]','Добавить журнал печати')
    Select(driver.find_element(By.CSS_SELECTOR,'#requestForm select[name=type]')).select_by_value('perfective')
    click(driver,'#requestForm button[type=submit]')
    check('Maintenance request created and dialog closes',lambda:(assert_eq(count(driver,'#requestTable tr'),5),assert_eq(driver.find_element(By.CSS_SELECTOR,'#new-request').get_attribute('open'),None)))
    screenshot(driver,'04-maintenance-1366.png')
    go(driver,'deployments.html')
    click(driver,'a[href="#new-deployment"]')
    fill(driver,'#deploymentForm input[name=client]','Тестовый отдел')
    fill(driver,'#deploymentForm input[name=product]','Портал тестирования')
    fill(driver,'#deploymentForm input[name=owner]','Студент')
    driver.execute_script("var n=document.querySelector('#deploymentForm input[name=plannedDate]');n.value='2026-12-01';n.dispatchEvent(new Event('change',{bubbles:true}))")
    click(driver,'#deploymentForm button[type=submit]')
    check('Deployment created and dialog closes',lambda:(assert_eq(count(driver,'#deploymentTable tr'),5),assert_eq(driver.find_element(By.CSS_SELECTOR,'#new-deployment').get_attribute('open'),None)))
    screenshot(driver,'02-deployments-1366.png')
    go(driver,'releases.html')
    click(driver,'a[href="#new-release"]')
    def semver():
        sel=Select(driver.find_element(By.CSS_SELECTOR,'#releaseLevel'))
        for level,expected in [('patch','v1.1.1'),('minor','v1.2.0'),('major','v2.0.0')]:
            sel.select_by_value(level)
            assert_eq(text(driver,'#nextVersion'),expected)
    check('SemVer patch/minor/major preview',semver)
    click(driver,'.dialog-close')
    screenshot(driver,'05-releases-1366.png')
    click(driver,'#themeButton')
    theme=driver.execute_script('return document.documentElement.dataset.theme')
    driver.refresh()
    check('Theme persists across reload',lambda:assert_eq(driver.execute_script('return document.documentElement.dataset.theme'),theme))
    driver.execute_script("localStorage.setItem('ssh.v1.incidents','{broken')")
    go(driver,'incidents.html')
    check('Corrupted localStorage is handled',lambda:assert_eq(count(driver,'#incidentTable tr'),6))
    check('Desktop no horizontal overflow',lambda:assert_eq(no_horizontal_overflow(driver),True))
    for name,width,height in [('tablet-768',768,1024),('mobile-390',390,844)]:
        driver.set_window_size(width,height)
        go(driver,'index.html')
        check(f'{width}px layout has no horizontal overflow',lambda:assert_eq(no_horizontal_overflow(driver),True))
        screenshot(driver,f'06-dashboard-{name}.png')
    check('Mobile menu button visible',lambda:assert_eq(driver.find_element(By.CSS_SELECTOR,'#menuToggle').is_displayed(),True))
    click(driver,'#menuToggle')
    check('Mobile sidebar opens',lambda:assert_eq('show' in driver.find_element(By.CSS_SELECTOR,'#sidebar').get_attribute('class'),True))
    errors=[e for e in driver.get_log('browser') if e.get('level')=='SEVERE']
    check('No severe JavaScript errors',lambda:assert_eq(errors,[]))
    driver.set_window_size(1366,900)
    go(driver,'incidents.html')
    click(driver,'a[href="#new-incident"]')
    screenshot(driver,'07-create-incident-dialog.png')
finally:
    driver.quit()
report={'date':datetime.now().isoformat(timespec='seconds'),'browser':'Google Chrome / Selenium (local HTTP server)','passed':sum(x['status']=='PASS' for x in results),'failed':sum(x['status']=='FAIL' for x in results),'results':results}
(ROOT/'tests'/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'tests'/'RESULTS.md').write_text('# Проверки интерфейса\n\n'+''.join('- **'+x['status']+'** '+x['test']+((' ('+x['details']+')') if x['details'] else '')+'\n' for x in results),encoding='utf-8')
print('FINAL',report['passed'],'PASS',report['failed'],'FAIL')
if report['failed']:raise SystemExit(1)
