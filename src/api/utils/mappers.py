from math import ceil

from ..schemas.articles import ArticleDetail, ArticleSummary, PaginationInfo


def to_article_summary(article) -> ArticleSummary:
    """Convert a database article model to ArticleSummary.

    Accepts any object with attributes used by the API schemas,
    keeping behavior identical to prior manual constructions.
    """
    return ArticleSummary(
        id=article.id,
        title=article.original_title,
        link=article.original_link,
        summary=article.original_summary,
        source=article.original_source,
        source_type=getattr(article, "source_type", None),
        published_date=getattr(article, "original_pubdate", None),
        created_at=article.created_at,
        image_url=getattr(article, "image_url", None),
    )


def to_article_detail(article) -> ArticleDetail:
    """Convert a database article model to ArticleDetail."""
    return ArticleDetail(
        id=article.id,
        title=article.original_title,
        link=article.original_link,
        summary=article.original_summary,
        source=article.original_source,
        source_type=getattr(article, "source_type", None),
        published_date=getattr(article, "original_pubdate", None),
        created_at=article.created_at,
        updated_at=getattr(article, "updated_at", None),
        processed=getattr(article, "processed", False),
        extracted_content=getattr(article, "extracted_content", None),
        ai_summary=getattr(article, "ai_summary", None),
        image_url=getattr(article, "image_url", None),
    )


def create_pagination_info(
    page: int, per_page: int, total_items: int
) -> PaginationInfo:
    """Create pagination metadata identical to previous logic."""
    total_pages = ceil(total_items / per_page) if total_items > 0 else 0
    return PaginationInfo(
        page=page,
        per_page=per_page,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
