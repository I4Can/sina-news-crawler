import random
def sina(lid,num, page, template_url):
    r=random.random()
    return template_url.format(lid,num,page,r)

def xinhua(lid,num,page,template_url):
    return template_url.format(lid,page,num)