import SwiftUI
import Combine

struct ArticleListView: View {
    @EnvironmentObject var apiService: APIService
    @State private var articles: [Article] = []
    @State private var currentPage = 1
    @State private var totalPages = 1
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var selectedSource: String?
    @State private var cancellables = Set<AnyCancellable>()

    private let perPage = 20

    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                if let errorMessage = errorMessage {
                    VStack {
                        Image(systemName: "exclamationmark.triangle")
                            .font(.largeTitle)
                            .foregroundColor(.orange)
                        Text("Error Loading Articles")
                            .font(.headline)
                        Text(errorMessage)
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                        Button("Retry") {
                            loadArticles()
                        }
                        .padding(.top)
                    }
                    .padding()
                } else {
                    List {
                        ForEach(articles) { article in
                            NavigationLink(destination: ArticleDetailView(articleId: article.id)) {
                                ArticleRowView(article: article)
                            }
                        }

                        if currentPage < totalPages {
                            Button(action: loadMoreArticles) {
                                if isLoading {
                                    ProgressView()
                                        .frame(maxWidth: .infinity)
                                } else {
                                    Text("Load More")
                                        .frame(maxWidth: .infinity)
                                }
                            }
                            .buttonStyle(.bordered)
                            .disabled(isLoading)
                        }
                    }
                    .refreshable {
                        await refreshArticles()
                    }
                }
            }
            .navigationTitle("Local News")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Menu {
                        Button("All Sources") {
                            selectedSource = nil
                            loadArticles()
                        }
                        Button("BBC News") {
                            selectedSource = "BBC News"
                            loadArticles()
                        }
                        Button("Manchester Evening News") {
                            selectedSource = "Manchester Evening News"
                            loadArticles()
                        }
                        Button("Nub News") {
                            selectedSource = "Nub News"
                            loadArticles()
                        }
                    } label: {
                        Image(systemName: "line.horizontal.3.decrease.circle")
                    }
                }
            }
        }
        .onAppear {
            if articles.isEmpty {
                loadArticles()
            }
        }
    }

    private func loadArticles() {
        isLoading = true
        errorMessage = nil
        currentPage = 1

        apiService.getArticles(
            page: currentPage,
            perPage: perPage,
            source: selectedSource,
            processedOnly: true
        )
        .sink(
            receiveCompletion: { completion in
                isLoading = false
                if case let .failure(error) = completion {
                    errorMessage = error.localizedDescription
                }
            },
            receiveValue: { paginatedArticles in
                articles = paginatedArticles.articles
                totalPages = paginatedArticles.pagination.totalPages
            }
        )
        .store(in: &cancellables)
    }

    private func loadMoreArticles() {
        guard !isLoading, currentPage < totalPages else { return }

        isLoading = true
        let nextPage = currentPage + 1

        apiService.getArticles(
            page: nextPage,
            perPage: perPage,
            source: selectedSource,
            processedOnly: true
        )
        .sink(
            receiveCompletion: { completion in
                isLoading = false
                if case let .failure(error) = completion {
                    errorMessage = error.localizedDescription
                }
            },
            receiveValue: { paginatedArticles in
                articles.append(contentsOf: paginatedArticles.articles)
                currentPage = nextPage
                totalPages = paginatedArticles.pagination.totalPages
            }
        )
        .store(in: &cancellables)
    }

    @MainActor
    private func refreshArticles() async {
        currentPage = 1

        do {
            let paginatedArticles = try await apiService.getArticles(
                page: currentPage,
                perPage: perPage,
                source: selectedSource,
                processedOnly: true
            )
            .async()

            articles = paginatedArticles.articles
            totalPages = paginatedArticles.pagination.totalPages
            errorMessage = nil
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

extension Publisher {
    func async() async throws -> Output {
        try await withCheckedThrowingContinuation { continuation in
            var cancellable: AnyCancellable?
            cancellable = self
                .sink(
                    receiveCompletion: { completion in
                        switch completion {
                        case .finished:
                            break
                        case .failure(let error):
                            continuation.resume(throwing: error)
                        }
                        cancellable?.cancel()
                    },
                    receiveValue: { value in
                        continuation.resume(returning: value)
                        cancellable?.cancel()
                    }
                )
        }
    }
}

#Preview {
    ArticleListView()
        .environmentObject(APIService.shared)
}
