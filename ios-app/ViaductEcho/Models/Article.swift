import Foundation

struct Article: Identifiable, Codable {
    let id: Int
    let title: String
    let link: String
    let summary: String
    let source: String
    let sourceType: String
    let publishedDate: Date
    let createdAt: Date
    let aiImageUrl: String?
    
    enum CodingKeys: String, CodingKey {
        case id
        case title
        case link
        case summary
        case source
        case sourceType = "source_type"
        case publishedDate = "published_date"
        case createdAt = "created_at"
        case aiImageUrl = "ai_image_url"
    }
}

struct ArticleDetail: Identifiable, Codable {
    let id: Int
    let title: String
    let link: String
    let summary: String
    let source: String
    let sourceType: String
    let publishedDate: Date
    let createdAt: Date
    let updatedAt: Date?
    let processed: Bool
    let extractedContent: String?
    let aiSummary: String?
    let aiImageUrl: String?
    
    enum CodingKeys: String, CodingKey {
        case id
        case title
        case link
        case summary
        case source
        case sourceType = "source_type"
        case publishedDate = "published_date"
        case createdAt = "created_at"
        case updatedAt = "updated_at"
        case processed
        case extractedContent = "extracted_content"
        case aiSummary = "ai_summary"
        case aiImageUrl = "ai_image_url"
    }
}

struct PaginatedArticles: Codable {
    let articles: [Article]
    let pagination: PaginationInfo
}

struct PaginationInfo: Codable {
    let page: Int
    let perPage: Int
    let totalItems: Int
    let totalPages: Int
    let hasNext: Bool
    let hasPrev: Bool
    
    enum CodingKeys: String, CodingKey {
        case page
        case perPage = "per_page"
        case totalItems = "total_items"
        case totalPages = "total_pages"
        case hasNext = "has_next"
        case hasPrev = "has_prev"
    }
}