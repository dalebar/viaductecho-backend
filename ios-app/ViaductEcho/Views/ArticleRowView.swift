import SwiftUI

struct ArticleRowView: View {
    let article: Article
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(article.source)
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.blue.opacity(0.1))
                    .cornerRadius(8)
                
                Spacer()
                
                Text(article.publishedDate, style: .relative)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Text(article.title)
                .font(.headline)
                .lineLimit(2)
                .multilineTextAlignment(.leading)
            
            if !article.summary.isEmpty {
                Text(article.summary)
                    .font(.body)
                    .foregroundColor(.secondary)
                    .lineLimit(3)
                    .multilineTextAlignment(.leading)
            }
            
            if let imageUrl = article.aiImageUrl, !imageUrl.isEmpty {
                AsyncImage(url: URL(string: imageUrl)) { image in
                    image
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                        .frame(height: 120)
                        .clipped()
                        .cornerRadius(8)
                } placeholder: {
                    Rectangle()
                        .fill(Color.gray.opacity(0.2))
                        .frame(height: 120)
                        .cornerRadius(8)
                        .overlay(
                            Image(systemName: "photo")
                                .foregroundColor(.gray)
                        )
                }
            }
        }
        .padding(.vertical, 4)
    }
}

#Preview {
    ArticleRowView(
        article: Article(
            id: 1,
            title: "Sample News Article Title That Might Be Quite Long",
            link: "https://example.com",
            summary: "This is a sample summary of the news article that provides context about what happened.",
            source: "BBC News",
            sourceType: "rss",
            publishedDate: Date().addingTimeInterval(-3600),
            createdAt: Date(),
            aiImageUrl: nil
        )
    )
    .padding()
}