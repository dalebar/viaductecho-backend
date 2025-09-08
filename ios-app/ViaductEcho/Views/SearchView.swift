import SwiftUI
import Combine

struct SearchView: View {
    @EnvironmentObject var apiService: APIService
    @State private var searchText = ""
    @State private var searchResults: [Article] = []
    @State private var recentArticles: [Article] = []
    @State private var currentPage = 1
    @State private var totalPages = 1
    @State private var isSearching = false
    @State private var isLoadingRecent = true
    @State private var errorMessage: String?
    @State private var cancellables = Set<AnyCancellable>()
    
    private let perPage = 20
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                SearchBar(text: $searchText, onSearchButtonClicked: performSearch)
                    .padding()
                
                if searchText.isEmpty {
                    recentArticlesView
                } else {
                    searchResultsView
                }
            }
            .navigationTitle("Search")
        }
        .onAppear {
            if recentArticles.isEmpty {
                loadRecentArticles()
            }
        }
    }
    
    private var recentArticlesView: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text("Recent Articles")
                    .font(.headline)
                    .padding(.horizontal)
                Spacer()
            }
            
            if isLoadingRecent {
                ProgressView()
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else if let errorMessage = errorMessage {
                VStack {
                    Image(systemName: "exclamationmark.triangle")
                        .font(.largeTitle)
                        .foregroundColor(.orange)
                    Text("Error Loading Recent Articles")
                        .font(.headline)
                    Text(errorMessage)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                    Button("Retry") {
                        loadRecentArticles()
                    }
                    .padding(.top)
                }
                .padding()
            } else {
                List(recentArticles) { article in
                    NavigationLink(destination: ArticleDetailView(articleId: article.id)) {
                        ArticleRowView(article: article)
                    }
                }
                .refreshable {
                    await refreshRecentArticles()
                }
            }
        }
    }
    
    private var searchResultsView: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text("Search Results")
                    .font(.headline)
                    .padding(.horizontal)
                Spacer()
                if !searchResults.isEmpty {
                    Text("\(searchResults.count) results")
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .padding(.horizontal)
                }
            }
            
            if isSearching {
                ProgressView()
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else if let errorMessage = errorMessage {
                VStack {
                    Image(systemName: "exclamationmark.triangle")
                        .font(.largeTitle)
                        .foregroundColor(.orange)
                    Text("Search Error")
                        .font(.headline)
                    Text(errorMessage)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                    Button("Try Again") {
                        performSearch()
                    }
                    .padding(.top)
                }
                .padding()
            } else if searchResults.isEmpty && !searchText.isEmpty {
                VStack {
                    Image(systemName: "magnifyingglass")
                        .font(.largeTitle)
                        .foregroundColor(.gray)
                    Text("No Results Found")
                        .font(.headline)
                    Text("Try different keywords or check your spelling")
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                }
                .padding()
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                List {
                    ForEach(searchResults) { article in
                        NavigationLink(destination: ArticleDetailView(articleId: article.id)) {
                            ArticleRowView(article: article)
                        }
                    }
                    
                    if currentPage < totalPages {
                        Button(action: loadMoreResults) {
                            if isSearching {
                                ProgressView()
                                    .frame(maxWidth: .infinity)
                            } else {
                                Text("Load More Results")
                                    .frame(maxWidth: .infinity)
                            }
                        }
                        .buttonStyle(.bordered)
                        .disabled(isSearching)
                    }
                }
            }
        }
    }
    
    private func performSearch() {
        guard !searchText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            return
        }
        
        isSearching = true
        errorMessage = nil
        currentPage = 1
        
        apiService.searchArticles(
            query: searchText,
            page: currentPage,
            perPage: perPage
        )
        .sink(
            receiveCompletion: { completion in
                isSearching = false
                if case let .failure(error) = completion {
                    errorMessage = error.localizedDescription
                }
            },
            receiveValue: { paginatedArticles in
                searchResults = paginatedArticles.articles
                totalPages = paginatedArticles.pagination.totalPages
            }
        )
        .store(in: &cancellables)
    }
    
    private func loadMoreResults() {
        guard !isSearching, currentPage < totalPages else { return }
        
        isSearching = true
        let nextPage = currentPage + 1
        
        apiService.searchArticles(
            query: searchText,
            page: nextPage,
            perPage: perPage
        )
        .sink(
            receiveCompletion: { completion in
                isSearching = false
                if case let .failure(error) = completion {
                    errorMessage = error.localizedDescription
                }
            },
            receiveValue: { paginatedArticles in
                searchResults.append(contentsOf: paginatedArticles.articles)
                currentPage = nextPage
                totalPages = paginatedArticles.pagination.totalPages
            }
        )
        .store(in: &cancellables)
    }
    
    private func loadRecentArticles() {
        isLoadingRecent = true
        errorMessage = nil
        
        apiService.getRecentArticles(hours: 24, limit: 50)
            .sink(
                receiveCompletion: { completion in
                    isLoadingRecent = false
                    if case let .failure(error) = completion {
                        errorMessage = error.localizedDescription
                    }
                },
                receiveValue: { articles in
                    recentArticles = articles
                }
            )
            .store(in: &cancellables)
    }
    
    @MainActor
    private func refreshRecentArticles() async {
        do {
            let articles = try await apiService.getRecentArticles(hours: 24, limit: 50).async()
            recentArticles = articles
            errorMessage = nil
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

struct SearchBar: View {
    @Binding var text: String
    var onSearchButtonClicked: () -> Void
    
    var body: some View {
        HStack {
            Image(systemName: "magnifyingglass")
                .foregroundColor(.secondary)
            
            TextField("Search articles...", text: $text)
                .textFieldStyle(PlainTextFieldStyle())
                .onSubmit {
                    onSearchButtonClicked()
                }
            
            if !text.isEmpty {
                Button(action: {
                    text = ""
                }) {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(10)
    }
}

#Preview {
    SearchView()
        .environmentObject(APIService.shared)
}