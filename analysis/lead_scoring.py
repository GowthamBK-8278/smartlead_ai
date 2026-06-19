def calculate_interest_score(comment):

    comment = comment.lower()

    keywords = [
        "interested",
        "join",
        "course",
        "admission",
        "fees",
        "details",
        "buy",
        "price"
    ]

    score = 20

    for word in keywords:

        if word in comment:
            score += 15

    return min(score, 100)


def get_sentiment(score):

    if score >= 80:
        return "Highly Interested"

    elif score >= 50:
        return "Interested"

    else:
        return "Low Interest"