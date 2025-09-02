import SwiftUI
import Combine

struct SourcesView: View {
    @EnvironmentObject var apiService: APIService
    @State private var sources: [Source] = []
    @State private var healthStatus: HealthStatus?
    @State private var isLoading = true
    @State private var errorMessage: String?
    @State private var cancellables = Set<AnyCancellable>()
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                if let healthStatus = healthStatus {
                    healthStatusView(healthStatus)
                }
                
                if isLoading {
                    ProgressView()
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if let errorMessage = errorMessage {
                    VStack {
                        Image(systemName: "exclamationmark.triangle")
                            .font(.largeTitle)
                            .foregroundColor(.orange)
                        Text("Error Loading Sources")
                            .font(.headline)
                        Text(errorMessage)
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                        Button("Retry") {
                            loadData()
                        }
                        .padding(.top)
                    }
                    .padding()
                } else {
                    List {
                        Section {
                            ForEach(sources) { source in
                                SourceRowView(source: source)
                            }
                        } header: {
                            Text("News Sources")
                        }
                    }
                    .refreshable {
                        await refreshData()
                    }
                }
            }
            .navigationTitle("Sources")
        }
        .onAppear {
            if sources.isEmpty {
                loadData()
            }
        }
    }
    
    private func healthStatusView(_ status: HealthStatus) -> some View {
        VStack(spacing: 8) {
            HStack {
                Circle()
                    .fill(status.isHealthy ? Color.green : Color.red)
                    .frame(width: 8, height: 8)
                
                Text(status.isHealthy ? "System Healthy" : "System Issues")
                    .font(.caption)
                    .foregroundColor(status.isHealthy ? .green : .red)
                    .fontWeight(.medium)
                
                Spacer()
                
                Text("Last updated: \(status.timestamp, style: .relative)")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            HStack(spacing: 20) {
                VStack {
                    Text("\(status.totalArticles)")
                        .font(.title2)
                        .fontWeight(.semibold)
                        .foregroundColor(.blue)
                    Text("Total Articles")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                VStack {
                    Text("\(status.recentArticles24h)")
                        .font(.title2)
                        .fontWeight(.semibold)
                        .foregroundColor(.green)
                    Text("Last 24h")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                VStack {
                    Image(systemName: status.databaseConnected ? "checkmark.circle.fill" : "xmark.circle.fill")
                        .font(.title2)
                        .foregroundColor(status.databaseConnected ? .green : .red)
                    Text("Database")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(8)
        .padding()
    }
    
    private func loadData() {
        isLoading = true
        errorMessage = nil
        
        let sourcesPublisher = apiService.getSources()
        let healthPublisher = apiService.getHealthStatus()
        
        Publishers.Zip(sourcesPublisher, healthPublisher)
            .sink(
                receiveCompletion: { completion in
                    isLoading = false
                    if case let .failure(error) = completion {
                        errorMessage = error.localizedDescription
                    }
                },
                receiveValue: { (sourcesData, healthData) in
                    sources = sourcesData
                    healthStatus = healthData
                }
            )
            .store(in: &cancellables)
    }
    
    @MainActor
    private func refreshData() async {
        do {
            async let sourcesData = apiService.getSources().async()
            async let healthData = apiService.getHealthStatus().async()
            
            let (newSources, newHealthStatus) = try await (sourcesData, healthData)
            
            sources = newSources
            healthStatus = newHealthStatus
            errorMessage = nil
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

#Preview {
    SourcesView()
        .environmentObject(APIService.shared)
}