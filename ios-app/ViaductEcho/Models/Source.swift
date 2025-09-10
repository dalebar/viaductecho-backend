import Foundation

struct Source: Identifiable, Codable {
    let id = UUID()
    let name: String
    let articleCount: Int
    let processedCount: Int
    let latestArticle: Date?

    enum CodingKeys: String, CodingKey {
        case name
        case articleCount = "article_count"
        case processedCount = "processed_count"
        case latestArticle = "latest_article"
    }

    var latestArticleFormatted: String {
        guard let latestArticle = latestArticle else {
            return "No articles"
        }

        let formatter = RelativeDateTimeFormatter()
        formatter.unitsStyle = .full
        return formatter.localizedString(for: latestArticle, relativeTo: Date())
    }

    var completionRate: Double {
        guard articleCount > 0 else { return 0.0 }
        return Double(processedCount) / Double(articleCount)
    }
}
