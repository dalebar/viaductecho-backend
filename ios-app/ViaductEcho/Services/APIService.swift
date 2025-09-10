import Foundation
import Combine

class APIService: ObservableObject {
    static let shared = APIService()

    private let baseURL = "http://localhost:8000/api/v1"
    private let session = URLSession.shared
    private let decoder: JSONDecoder

    private init() {
        self.decoder = JSONDecoder()
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        decoder.dateDecodingStrategy = .custom { decoder in
            let container = try decoder.singleValueContainer()
            let dateString = try container.decode(String.self)

            if let date = formatter.date(from: dateString) {
                return date
            }

            let fallbackFormatter = ISO8601DateFormatter()
            if let date = fallbackFormatter.date(from: dateString) {
                return date
            }

            throw DecodingError.dataCorruptedError(
                in: container,
                debugDescription: "Invalid date format: \(dateString)"
            )
        }
    }

    func getArticles(
        page: Int = 1,
        perPage: Int = 20,
        source: String? = nil,
        processedOnly: Bool = true
    ) -> AnyPublisher<PaginatedArticles, Error> {
        var components = URLComponents(string: "\(baseURL)/articles")!
        components.queryItems = [
            URLQueryItem(name: "page", value: String(page)),
            URLQueryItem(name: "per_page", value: String(perPage)),
            URLQueryItem(name: "processed_only", value: String(processedOnly))
        ]

        if let source = source {
            components.queryItems?.append(URLQueryItem(name: "source", value: source))
        }

        guard let url = components.url else {
            return Fail(error: URLError(.badURL))
                .eraseToAnyPublisher()
        }

        return session.dataTaskPublisher(for: url)
            .map(\.data)
            .decode(type: PaginatedArticles.self, decoder: decoder)
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }

    func getRecentArticles(
        hours: Int = 24,
        limit: Int = 50
    ) -> AnyPublisher<[Article], Error> {
        var components = URLComponents(string: "\(baseURL)/articles/recent")!
        components.queryItems = [
            URLQueryItem(name: "hours", value: String(hours)),
            URLQueryItem(name: "limit", value: String(limit))
        ]

        guard let url = components.url else {
            return Fail(error: URLError(.badURL))
                .eraseToAnyPublisher()
        }

        return session.dataTaskPublisher(for: url)
            .map(\.data)
            .decode(type: [Article].self, decoder: decoder)
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }

    func searchArticles(
        query: String,
        page: Int = 1,
        perPage: Int = 20
    ) -> AnyPublisher<PaginatedArticles, Error> {
        var components = URLComponents(string: "\(baseURL)/articles/search")!
        components.queryItems = [
            URLQueryItem(name: "query", value: query),
            URLQueryItem(name: "page", value: String(page)),
            URLQueryItem(name: "per_page", value: String(perPage))
        ]

        guard let url = components.url else {
            return Fail(error: URLError(.badURL))
                .eraseToAnyPublisher()
        }

        return session.dataTaskPublisher(for: url)
            .map(\.data)
            .decode(type: PaginatedArticles.self, decoder: decoder)
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }

    func getArticle(id: Int) -> AnyPublisher<ArticleDetail, Error> {
        guard let url = URL(string: "\(baseURL)/articles/\(id)") else {
            return Fail(error: URLError(.badURL))
                .eraseToAnyPublisher()
        }

        return session.dataTaskPublisher(for: url)
            .map(\.data)
            .decode(type: ArticleDetail.self, decoder: decoder)
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }

    func getSources() -> AnyPublisher<[Source], Error> {
        guard let url = URL(string: "\(baseURL)/sources") else {
            return Fail(error: URLError(.badURL))
                .eraseToAnyPublisher()
        }

        return session.dataTaskPublisher(for: url)
            .map(\.data)
            .decode(type: [Source].self, decoder: decoder)
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }

    func getHealthStatus() -> AnyPublisher<HealthStatus, Error> {
        guard let url = URL(string: "http://localhost:8000/health") else {
            return Fail(error: URLError(.badURL))
                .eraseToAnyPublisher()
        }

        return session.dataTaskPublisher(for: url)
            .map(\.data)
            .decode(type: HealthStatus.self, decoder: decoder)
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }
}

struct HealthStatus: Codable {
    let status: String
    let totalArticles: Int
    let recentArticles24h: Int
    let databaseConnected: Bool
    let timestamp: Date

    enum CodingKeys: String, CodingKey {
        case status
        case totalArticles = "total_articles"
        case recentArticles24h = "recent_articles_24h"
        case databaseConnected = "database_connected"
        case timestamp
    }

    var isHealthy: Bool {
        status == "healthy" && databaseConnected
    }
}
