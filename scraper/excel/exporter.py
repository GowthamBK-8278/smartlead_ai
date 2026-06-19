import os

def export_to_excel(df, domain):

    os.makedirs(
        "data/reports",
        exist_ok=True
    )

    file_name = (
        f"data/reports/{domain}_leads.xlsx"
    )

    df.to_excel(
        file_name,
        index=False
    )

    return file_name