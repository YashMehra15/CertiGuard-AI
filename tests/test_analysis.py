from backend.app.services.analysis import detect_issuer,extract_id,extract_fields

def test_nptel():
    text='Programming in Java\nYASH MEHRA\nJan-Apr 2026\nNPTEL26CS36S855900156'
    cid=extract_id(text,[],"NPTEL",['https://nptel.ac.in/noc/E_Certificate/NPTEL26CS36S85590015604950397'])
    assert cid=='NPTEL26CS36S85590015604950397'
    f=extract_fields(text,"NPTEL");assert f['student_name']=='YASH MEHRA'

def test_saylor():
    text='Yash4367ssgk Mehra\nCS107: C++ Programming\n25 April 2025\n5484755338YM\n40 Hours\n87.50'
    assert extract_id(text,['https://learn.saylor.org/admin/tool/certificate/index.php?code=5484755338YM'],'Saylor Academy',[])=='5484755338YM'
    f=extract_fields(text,'Saylor Academy');assert f['course_line']=='CS107: C++ Programming'

def test_av():
    text='Awarded to Yash4367ssgk For successfully completing the Free Course Generative AI with AWS 2026-02-17 ivhes8hjkt'
    assert detect_issuer(text,[])=='Analytics Vidhya'
    f=extract_fields(text,'Analytics Vidhya');assert f['course_line']=='Generative AI with AWS'

def test_nptel_issue_date():
    text='Developing Soft Skills and Personality\nYASH MEHRA\nAug-Oct 2024\n(8 week course)\nNPTEL24HS176S55420019904334812'
    f=extract_fields(text,'NPTEL')
    assert f['student_name']=='YASH MEHRA'
    assert f['course_line']=='Developing Soft Skills and Personality'
    assert f['issue_date'] is None or isinstance(f['issue_date'], str)

def test_nielit_fields():
    text='National Institute of Electronics and Information Technology (NIELIT)\nCertificate No. : 2026071445419408-172715\nThis is to certify that Mr./Ms./Mx.\nYash Mehra\nEmbedded Assessment\nYuva AI for All 2\n4 Hours 30 Minutes 0.15 Online\nNew Delhi 14/07/2026'
    f=extract_fields(text,'NIELIT')
    assert f['student_name']=='Yash Mehra'
    assert f['course_line']=='Yuva AI for All'
    assert f['issue_date']=='14/07/2026'
    assert f['duration']=='4 Hours 30 Minutes'

def test_swayam_fields():
    text='SWAYAM ONLINE COURSE CERTIFICATION\nThis Certificate is awarded to\nYASH MEHRA\nRoll No:UK02010135\nfor successfully completing the 4 credit course Fundamentals of Financial Inclusion and Cyber Safety with a consolidated score of 86% marks\nIssued On: 21/01/2026'
    f=extract_fields(text,'SWAYAM')
    assert f['student_name']=='YASH MEHRA'
    assert f['course_line']=='Fundamentals of Financial Inclusion and Cyber Safety'
    assert f['issue_date']=='21/01/2026'
    assert f['grade']=='86%'


def test_account_independence():
    text='NPTEL\nProgramming in Java\nYASH MEHRA\nJan-Apr 2026\n(12 week course)\nNPTEL26CS36S855900156'
    from backend.app.services.analysis import analyze
    result=analyze(text.encode(), 'certificate.pdf', [], 'Different User', 'BCA')
    assert not any('Registered' in e['name'] for e in result['evidence'])
    assert not any('registered student' in x.lower() or 'registered course' in x.lower() for x in result['concrete_tamper_signals'])
