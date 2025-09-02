import SwiftUI

struct SourceRowView: View {
    let source: Source
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                VStack(alignment: .leading) {
                    Text(source.name)
                        .font(.headline)
                        .foregroundColor(.primary)
                    
                    Text(source.latestArticleFormatted)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                VStack(alignment: .trailing) {
                    Text("\(source.articleCount)")
                        .font(.title2)
                        .fontWeight(.semibold)
                        .foregroundColor(.blue)
                    
                    Text("articles")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
            VStack(spacing: 8) {
                HStack {
                    Text("Processing Status")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    
                    Spacer()
                    
                    Text("\(source.processedCount)/\(source.articleCount)")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                ProgressView(value: source.completionRate)
                    .progressViewStyle(LinearProgressViewStyle(tint: source.completionRate == 1.0 ? .green : .blue))
                    .scaleEffect(x: 1, y: 0.8)
            }
        }
        .padding(.vertical, 4)
    }
}

#Preview {
    VStack {
        SourceRowView(
            source: Source(
                name: "BBC News",
                articleCount: 150,
                processedCount: 145,
                latestArticle: Date().addingTimeInterval(-3600)
            )
        )
        .padding()
        
        Divider()
        
        SourceRowView(
            source: Source(
                name: "Manchester Evening News",
                articleCount: 89,
                processedCount: 78,
                latestArticle: Date().addingTimeInterval(-7200)
            )
        )
        .padding()
        
        Divider()
        
        SourceRowView(
            source: Source(
                name: "Stockport Nub News",
                articleCount: 45,
                processedCount: 45,
                latestArticle: nil
            )
        )
        .padding()
    }
}