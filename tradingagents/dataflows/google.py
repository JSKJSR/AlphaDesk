from typing import Annotated
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .googlenews_utils import getNewsData


def get_google_news(
    query: Annotated[str, "Query to search with"],
    curr_date_or_start: Annotated[str, "Curr date or start date in yyyy-mm-dd format"],
    look_back_days_or_end: Annotated[str | int, "days to look back (int) or end date (str)"] = 7,
) -> str:
    """
    Retrieve Google News for a query.

    This function supports two calling conventions:
    1. (query, curr_date, look_back_days) - looks back N days from curr_date
    2. (ticker, start_date, end_date) - searches between start_date and end_date

    Args:
        query: Search query or ticker symbol
        curr_date_or_start: Current date or start date in yyyy-mm-dd format
        look_back_days_or_end: Either days to look back (int) or end date (str)

    Returns:
        Formatted string of news results
    """
    query = query.replace(" ", "+")

    # Detect which calling convention is being used
    if isinstance(look_back_days_or_end, int):
        # Convention 1: (query, curr_date, look_back_days)
        curr_date = curr_date_or_start
        look_back_days = look_back_days_or_end
        end_date = datetime.strptime(curr_date, "%Y-%m-%d")
        start_date = end_date - relativedelta(days=look_back_days)
        before = start_date.strftime("%Y-%m-%d")
        after = curr_date
    else:
        # Convention 2: (ticker, start_date, end_date)
        # look_back_days_or_end is actually the end_date string
        before = curr_date_or_start  # This is start_date
        after = str(look_back_days_or_end)  # This is end_date

    news_results = getNewsData(query, before, after)

    news_str = ""
    for news in news_results:
        news_str += (
            f"### {news['title']} (source: {news['source']}) \n\n{news['snippet']}\n\n"
        )

    if len(news_results) == 0:
        return f"No Google News found for {query} from {before} to {after}."

    return f"## {query} Google News, from {before} to {after}:\n\n{news_str}"


def get_google_global_news(
    curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "Number of days to look back"] = 7,
    limit: Annotated[int, "Maximum number of articles to return"] = 5,
) -> str:
    """
    Retrieve global market news from Google News.

    This is an adapter function that wraps get_google_news for global news queries.

    Args:
        curr_date: Current date in yyyy-mm-dd format
        look_back_days: Number of days to look back (default 7)
        limit: Maximum number of articles to return (default 5)

    Returns:
        Formatted string of global news results
    """
    # Use a broad market query for global news
    query = "global stock market news"

    end_date = datetime.strptime(curr_date, "%Y-%m-%d")
    start_date = end_date - relativedelta(days=look_back_days)
    before = start_date.strftime("%Y-%m-%d")
    after = curr_date

    news_results = getNewsData(query.replace(" ", "+"), before, after)

    # Limit results
    news_results = news_results[:limit] if len(news_results) > limit else news_results

    news_str = ""
    for news in news_results:
        news_str += (
            f"### {news['title']} (source: {news['source']}) \n\n{news['snippet']}\n\n"
        )

    if len(news_results) == 0:
        return f"No global news found from {before} to {after}."

    return f"## Global Market News, from {before} to {after}:\n\n{news_str}"
