# Viaduct Echo iOS App

A native iOS news reader app built with SwiftUI that displays local Greater Manchester news aggregated by the Viaduct Echo backend system.

## Features

### Core Functionality
- **Article Browse**: Paginated list of local news articles with infinite scroll
- **Search**: Full-text search across article titles, summaries, and content
- **Article Details**: Complete article view with AI summaries and extracted content
- **Source Filtering**: Filter articles by news source (BBC, MEN, Nub News)
- **System Status**: Real-time API health monitoring and source statistics

### User Experience
- **Native iOS Design**: Built with SwiftUI following iOS design guidelines
- **Offline-Ready**: Graceful error handling and retry mechanisms
- **Performance**: Efficient API calls with proper pagination and caching
- **Accessibility**: Standard iOS accessibility features supported

## Architecture

### SwiftUI + Combine
- Reactive UI updates using `@StateObject` and `@EnvironmentObject`
- Combine publishers for API integration
- Modern async/await patterns for cleaner asynchronous code

### Project Structure
```
ViaductEcho/
├── Models/
│   ├── Article.swift          # Article data models
│   └── Source.swift           # Source data models
├── Services/
│   └── APIService.swift       # REST API integration
├── Views/
│   ├── ArticleListView.swift  # Main article listing
│   ├── ArticleDetailView.swift # Article details
│   ├── ArticleRowView.swift   # Article list row component
│   ├── SearchView.swift       # Search interface
│   ├── SourcesView.swift      # Sources overview
│   └── SourceRowView.swift    # Source list row component
├── ViaductEchoApp.swift       # App entry point
└── ContentView.swift          # Tab navigation
```

## API Integration

### Endpoints Used
- `GET /api/v1/articles` - Paginated article listing
- `GET /api/v1/articles/recent` - Recent articles (24h)
- `GET /api/v1/articles/search` - Article search
- `GET /api/v1/articles/{id}` - Article details
- `GET /api/v1/sources` - Source statistics
- `GET /health` - API health check

### Configuration
The app connects to the local development server at `http://localhost:8000` by default. This can be modified in `APIService.swift`:

```swift
private let baseURL = "http://localhost:8000/api/v1"
```

For production deployment, update this to your production API URL.

## Development Setup

### Prerequisites
- Xcode 15.0+ (supports iOS 16.0+)
- iOS Simulator or physical device
- Viaduct Echo backend API running locally

### Getting Started

1. **Start the Backend API**
   ```bash
   # From the project root
   python -m src.main
   # or
   uvicorn src.api.app:app --reload
   ```

2. **Open in Xcode**
   ```bash
   open ios-app/ViaductEcho.xcodeproj
   ```

3. **Build and Run**
   - Select your target device/simulator
   - Press ⌘+R to build and run

### Network Configuration

For iOS Simulator testing with localhost:
- The app uses `http://localhost:8000` which works with iOS Simulator
- For physical device testing, replace `localhost` with your machine's IP address

### Testing on Device
If testing on a physical device, update the API base URL:
```swift
// In APIService.swift, replace:
private let baseURL = "http://localhost:8000/api/v1"
// With your machine's IP:
private let baseURL = "http://192.168.1.100:8000/api/v1"
```

## Key Components

### APIService
Handles all REST API communication using Combine publishers:
- Automatic JSON decoding with custom date parsing
- Error handling and retry logic
- Pagination support
- Health monitoring

### ArticleListView
Main article browsing interface:
- Pull-to-refresh functionality
- Infinite scroll pagination
- Source filtering menu
- Navigation to article details

### SearchView
Search interface with dual modes:
- Recent articles when search is empty
- Search results with pagination
- Real-time search as you type

### SourcesView
System overview dashboard:
- API health status indicator
- Source statistics and processing rates
- Real-time data refresh

## Deployment Considerations

### Production Configuration
- Update API base URL to production server
- Configure proper SSL certificates
- Add app icons and launch screens
- Set up proper bundle identifiers

### App Store Preparation
- Add required privacy descriptions in Info.plist
- Configure app metadata and screenshots
- Set up proper code signing
- Test on multiple device sizes

## Future Enhancements

### Planned Features
- **Push Notifications**: Real-time alerts for breaking news
- **Offline Reading**: Cache articles for offline access
- **Dark Mode**: Enhanced dark mode support
- **Customization**: User preferences for sources and topics
- **Share Extension**: Share articles to social media
- **Widget Support**: Home screen widgets for latest news

### Technical Improvements
- **Core Data**: Local persistence layer
- **Background Sync**: Background app refresh for new content
- **Image Caching**: Efficient image loading and caching
- **Analytics**: User engagement tracking
- **Performance Monitoring**: Crash reporting and performance metrics

## Dependencies

### System Frameworks
- SwiftUI (iOS 16.0+)
- Combine (iOS 16.0+)
- Foundation (URL handling, JSON)

### Third-Party
No external dependencies - uses only native iOS frameworks for maximum compatibility and minimal app size.

## Contributing

### Code Style
- Follow Swift naming conventions
- Use SwiftUI best practices
- Maintain consistent indentation (4 spaces)
- Add meaningful comments for complex logic

### Testing
- Test on multiple device sizes (iPhone SE to iPhone 15 Pro Max)
- Verify both light and dark mode appearances
- Test with poor network conditions
- Validate accessibility features

This iOS app provides a complete native interface to the Viaduct Echo news aggregation system, offering users an intuitive way to stay informed about Greater Manchester local news.