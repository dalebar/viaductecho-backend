import SwiftUI
import Combine

struct ArticleDetailView: View {
    let articleId: Int
    @EnvironmentObject var apiService: APIService
    @State private var article: ArticleDetail?
    @State private var isLoading = true
    @State private var errorMessage: String?
    @State private var cancellables = Set<AnyCancellable>()
    
    var body: some View {
        ScrollView {
            if isLoading {
                VStack {
                    ProgressView()
                        .padding()
                    Text("Loading article...")
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else if let errorMessage = errorMessage {
                VStack(spacing: 16) {
                    Image(systemName: "exclamationmark.triangle")
                        .font(.largeTitle)
                        .foregroundColor(.orange)
                    Text("Error Loading Article")
                        .font(.headline)
                    Text(errorMessage)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                    Button("Retry") {
                        loadArticle()
                    }
                }
                .padding()
            } else if let article = article {
                VStack(alignment: .leading, spacing: 16) {
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
                            
                            Text(article.publishedDate, style: .date)
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        
                        Text(article.title)
                            .font(.largeTitle)
                            .fontWeight(.bold)
                            .multilineTextAlignment(.leading)
                    }
                    
                    if let imageUrl = article.aiImageUrl, !imageUrl.isEmpty {
                        AsyncImage(url: URL(string: imageUrl)) { image in
                            image
                                .resizable()
                                .aspectRatio(contentMode: .fit)
                                .cornerRadius(8)
                        } placeholder: {
                            Rectangle()
                                .fill(Color.gray.opacity(0.2))
                                .aspectRatio(16/9, contentMode: .fit)
                                .cornerRadius(8)
                                .overlay(
                                    ProgressView()
                                )
                        }
                    }
                    
                    if !article.summary.isEmpty {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Summary")
                                .font(.headline)
                            Text(article.summary)
                                .font(.body)
                                .foregroundColor(.primary)
                        }
                    }
                    
                    if let aiSummary = article.aiSummary, !aiSummary.isEmpty {
                        VStack(alignment: .leading, spacing: 8) {
                            HStack {
                                Image(systemName: "sparkles")
                                    .foregroundColor(.purple)
                                Text("AI Summary")
                                    .font(.headline)
                                    .foregroundColor(.purple)
                            }
                            Text(aiSummary)
                                .font(.body)
                                .padding()
                                .background(Color.purple.opacity(0.1))
                                .cornerRadius(8)
                        }
                    }
                    
                    if let extractedContent = article.extractedContent, !extractedContent.isEmpty {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Full Article")
                                .font(.headline)
                            Text(extractedContent)
                                .font(.body)
                                .lineLimit(nil)
                        }
                    }
                    
                    Link(destination: URL(string: article.link)!) {
                        HStack {
                            Image(systemName: "safari")
                            Text("Read Original Article")
                        }
                        .foregroundColor(.blue)
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(Color.blue.opacity(0.1))
                        .cornerRadius(8)
                    }
                    
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Article Info")
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .textCase(.uppercase)
                        
                        HStack {
                            Text("Source:")
                            Text(article.source)
                                .fontWeight(.medium)
                        }
                        .font(.caption)
                        
                        HStack {
                            Text("Published:")
                            Text(article.publishedDate, style: .date)
                                .fontWeight(.medium)
                        }
                        .font(.caption)
                    }
                    .padding()
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(8)
                }
                .padding()
            }
        }
        .navigationBarTitleDisplayMode(.inline)
        .onAppear {
            loadArticle()
        }
    }
    
    private func loadArticle() {
        isLoading = true
        errorMessage = nil
        
        apiService.getArticle(id: articleId)
            .sink(
                receiveCompletion: { completion in
                    isLoading = false
                    if case let .failure(error) = completion {
                        errorMessage = error.localizedDescription
                    }
                },
                receiveValue: { articleDetail in
                    article = articleDetail
                }
            )
            .store(in: &cancellables)
    }
}

#Preview {
    NavigationView {
        ArticleDetailView(articleId: 1)
            .environmentObject(APIService.shared)
    }
}