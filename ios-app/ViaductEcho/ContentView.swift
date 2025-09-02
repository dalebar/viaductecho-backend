import SwiftUI

struct ContentView: View {
    var body: some View {
        TabView {
            ArticleListView()
                .tabItem {
                    Image(systemName: "newspaper")
                    Text("Articles")
                }
            
            SearchView()
                .tabItem {
                    Image(systemName: "magnifyingglass")
                    Text("Search")
                }
            
            SourcesView()
                .tabItem {
                    Image(systemName: "globe")
                    Text("Sources")
                }
        }
        .accentColor(.blue)
    }
}

#Preview {
    ContentView()
        .environmentObject(APIService.shared)
}