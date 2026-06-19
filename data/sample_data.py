import pandas as pd

def get_sample_data(domain):

    data = {
        "Aviation": [
            ["YouTube", "Pilot Training Course",
             "aviation_dreamer",
             "Interested in becoming a pilot"],
            ["Instagram", "Flight School",
             "future_pilot_2026",
             "Need aviation course details"],
            ["Facebook", "Aviation Academy",
             "pilot_career_goal",
             "How much are the fees?"]
        ],

        "Laptops": [

    ["YouTube",
     "Gaming Laptop Review",
     "coding_student_01",
     "Need laptop for coding"],

    ["Instagram",
     "Dell Laptop",
     "tech_buyer_22",
     "Interested in buying"],

    ["Facebook",
     "HP Laptop",
     "laptop_hunter",
     "Battery backup review"]

],

       "Colleges": [

    ["YouTube",
     "Engineering Admission",
     "future_engineer",
     "Need college details"],

    ["Instagram",
     "MBA Program",
     "mba_aspirant",
     "Interested in MBA"],

    ["Facebook",
     "Scholarship Post",
     "scholarship_seeker",
     "Need scholarship info"]

]
    }

    df_data = data.get(domain, [])
    cols = ["Platform", "Title", "Username", "Comment"] if len(df_data) > 0 and len(df_data[0]) == 4 else ["Platform", "Title", "Comment"]
    return pd.DataFrame(df_data, columns=cols)