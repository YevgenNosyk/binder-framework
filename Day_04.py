
import pandas as pd

#special print routine for dataframes and ndarrays: uses "\n\n" as separator 
#and end of printout
prn = lambda *args: print(*args, sep = "\n\n", end = "\n\n")


df = pd.read_csv(
    "Value_of_Energy_Cost_Savings_Program_Savings_for_Businesses_-_FY2020.csv", 
    parse_dates = ["Effective Date"])


#replacing whitespaces with _ makes field names accessible as df attributes
#df = df.rename(  
#    columns = {field : field.replace(" ", "_") for field in df.keys()}
#    )  

#simpler, but the same effect
df = df.rename(columns = lambda s: str.replace(s, " ", "_"))




#------------Q1: How many different companies

#count and check if there are any NA's
cnt = df.Company_Name.count()
print(cnt, cnt == df.shape[0])  



#Q1.1: simple query of all distinct company names as is, 
#not accounting for possible different spellings of the same company name.

#ANSWER Q1:
unique_simple = df.Company_Name.drop_duplicates()   
print("ANS Q1: Number of different companies (not accounting for spelling):",unique_simple.count())




#Q1.2: preprocessing company names to account for some possible spelling differences.
#Assume: only characters from directly accessible from keyboard are allowed, 
#and simple ASCII characters.

#simple visual check that ' symbol is only used as apostrophe, not a quote mark
prn(df.Company_Name[df.Company_Name.str.contains("'")]) 


c_names = df.Company_Name.str.lower()   #all names to lower case

#replace all punctuation accessible from keyboard, except ' , with a space " "
c_names = c_names.str.replace(r'[~`!@#$%^&*()_+={}[|:;"<,>.?/\-\]\\]', " ", regex=True)

c_names = c_names.str.strip()   #strip all whitespace chars from ends

#replace multiple space chars with a single space " "
c_names = c_names.str.replace(r"\s+", " ", regex=True)

#Now we should have lower case words (digits and ' allowed) separated by single spaces
prn(c_names)

unique_processed = c_names.drop_duplicates()

#ANSWER Q1:
print("ANS Q1: Number of different companies (accounting for some possible spelling differences):", 
unique_processed.count())

#A simple check that indexes of unique names match for unprocessed and processed cases.
#If they don't (False), we should look further into it.
prn((unique_simple.index == unique_processed.index).all())

#<


#----------- Q2: Total number of jobs for businesses in Queens

#Note: the question is ambiguous: it's not clear whether Queens stands for City or Borough field.
#However, it's easy to implement both.

#ANSWER Q2:
print("ANS Q2: Total number of jobs created in the *city* of Queens:", df[df.City == 'Queens'].Job_created.sum())
print("ANS Q2: Total number of jobs created in the *borough* of Queens:", df[df.Borough == 'Queens'].Job_created.sum())



#<

#----------- Q3: Number of different unique email domains

#Assumptions: 
#   1) valid emails have format:  local_part@domain
#   2) we ignore fairly complex rules for acceptable local_part, since we only want domain names
#   3) domain names are (as per https://en.wikipedia.org/wiki/Email_address#Domain)
#   lists of . separated DNS names; each label is less than 63 characters, which are:
#       3.1) uppercase and lowercase Latin letters A to Z and a to z;
#       3.2) digits 0 to 9, provided that top-level domain names are not all-numeric;
#       3.3) hyphen -, provided that it is not the first or last character.
#   4) We also assume no single-label domain names, and no ip-adresses.




#check that company_contact field doesn't contain some emails by accident
print(df.company_contact.str.contains("@").any()) 
#The output suggests it doesn't so we ignore it from now on.


emails = df.company_email.dropna()
print(emails.count())

emails = emails.str.strip() #ignore leading and trailing whitespace-like chars

#print(emails[emails.str.contains("@")].count())

#valid email has at least one @. The last @ is followed by domain name.
domains = emails[emails.str.contains("@")].str.split("@").str.get(-1)
prn(domains)

#ANSWER Q3: 
print("ANS Q3: Number of unique domain names, without checking their validity:", 
    domains.drop_duplicates().count())
    
#Implement function checking assumptions 3-4 above for a domain name.
def check_domain_name(dmn: str) -> bool:
    """Returns True, if assumptions 3-4 satisfied."""
    labels = dmn.split(".")
    for label in labels:
        # no labels of 0 or >63 length; no labels starting or ending with -
        length = len(label)
        if  length == 0 or length > 63 or label[0] == '-' or label[-1] == '-':
            return False
        
        # only numbers and letters besides -
        if not label.replace("-", "1").isalnum():
            return False
        
    #Top level domain label can't be all numbers
    if labels[-1].isdecimal():
        return False
    
    #all checks passed.
    return True
    

#!! debug
if False:
    print(check_domain_name("12.asd-dfg"))
    print(check_domain_name("-12.asd-dfg"))
    print(check_domain_name("12-.asd-dfg.co1m"))
    print(check_domain_name("12-.asd-dfg.012"))
    print(check_domain_name("123456789012345678901234567890"
                        "123456789012345678901234567890123.asd-dfg"))
    print(check_domain_name("123456789012345678901234567890"
                        "1234567890123456789012345678901234.asd-dfg"))
        
#!! debug
prn(domains[domains.apply(check_domain_name) == False])

valid_domains = domains[domains.apply(check_domain_name)]
prn(valid_domains, valid_domains.count())

#ANSWER Q3: 
print("ANS Q3: Number of unique *valid* domain names:", valid_domains.drop_duplicates().count())

#<




#----------- Q4: For *each* NTA with at least 5 businesses, total savings and total jobs created

#Side Note: NTA = Neighborhood Tabulation Areas

#Assumptions: exlude records where NTA is nan

#>

#----Table of distinct businesses counts for each NTA.
#NOTE: need to take into accout that the same business can possibly have different NTAs,
#e.g. if it moved. 

#NOTE: preprocessing Company_Name did not give different results for distinct business count.
#So, Company_Name preprocessing won't make difference for this question either.

nta_business_counts = df.drop_duplicates(subset = ["Company_Name", "NTA"]).groupby("NTA").Company_Name.count()
prn(nta_business_counts, nta_business_counts[nta_business_counts>=5])   




#----Table of savings and jobs created for each NTA

nta_savings_jobs = df.groupby("NTA").agg({"Total_Savings":"mean", "Job_created":"sum"})
prn(nta_savings_jobs)

#add 1st table into 2nd. This matches the idices (NTAs) of dataframe and series.
nta_savings_jobs["Business_count"] = nta_business_counts    
prn(nta_savings_jobs)

#Edit names and types of some fields before saving
#Side Note: .astype() doesn't seem to do in-place type conversion with copy=False. Hence the previous line with reassigning.
#Possibly a bug, as per https://stackoverflow.com/questions/41566760/bug-on-astype-pandas ?
nta_savings_jobs.rename(columns = {"Total_Savings":"Average_total_savings", "Job_created":"Total_jobs_created"}, inplace = True)
nta_savings_jobs.Total_jobs_created = nta_savings_jobs.Total_jobs_created.astype("int32")


#This is not the final answer to questions 4 and 5 yet, but we will use this file for Day 5.
nta_savings_jobs.to_csv("Q4_out_aux.csv", index = True)


#only need NTAs with >=5 businesses
nta_savings_jobs = nta_savings_jobs[nta_savings_jobs.Business_count >= 5]



#ANSWER Q4
prn("\n\nANS Q4:", nta_savings_jobs)



#--------Q5: Saving results of Q4 to csv

nta_savings_jobs.to_csv("Q4_out.csv", index = True)


print("AAAAAAAAAA")