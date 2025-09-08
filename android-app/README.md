# Viaduct Echo Android App

A native Android application for the Viaduct Echo news aggregation platform, built with modern Android development practices and Material Design 3.

## 🏗️ Architecture

- **MVVM Architecture** with ViewModels and LiveData
- **Hilt Dependency Injection** for clean separation of concerns
- **Repository Pattern** for data management
- **Navigation Component** with type-safe arguments
- **Retrofit** for API communication
- **Glide** for optimized image loading
- **Room** for offline capability (optional)

## 🎨 Design

- **Material Design 3** theming system
- **Dynamic Color** support (Android 12+)
- **Dark Theme** compatibility
- **Accessibility** compliant (TalkBack, large text, etc.)
- **Responsive Layouts** for different screen sizes

## 📱 Features

### Core Functionality
- **Article List** with infinite scroll pagination
- **Article Detail** view with AI summaries
- **Pull-to-refresh** for latest content
- **Offline handling** with cached content
- **Share articles** via system share sheet
- **External links** to original articles

### Performance
- **Image caching** with Glide optimization
- **Memory efficient** RecyclerView with ViewBinding
- **Network connectivity** monitoring
- **Smooth animations** and transitions
- **Lazy loading** of non-critical components

### Accessibility
- **TalkBack support** with descriptive content
- **Focus management** for keyboard navigation
- **High contrast** color schemes
- **Large text** scaling support
- **Touch target** sizing (min 48dp)

## 🛠️ Development Setup

### Prerequisites
- Android Studio Arctic Fox or later
- Android SDK 24+ (supports Android 7.0+)
- Kotlin 1.9+
- Gradle 8.0+

### Configuration

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd viaductecho-backend/android-app
   ```

2. **API Configuration**:
   Update `BuildConfig.API_BASE_URL` in `build.gradle.kts`:
   ```kotlin
   buildConfigField("String", "API_BASE_URL", "\"http://your-api-server.com\"")
   ```

3. **Build variants**:
   - `debug`: Uses localhost API (10.0.2.2:8000 for emulator)
   - `release`: Uses production API URL

## 🏃‍♂️ Running the App

### Debug Build
```bash
./gradlew assembleDebug
./gradlew installDebug
```

### Release Build
```bash
./gradlew assembleRelease
```

### Testing
```bash
# Unit tests
./gradlew testDebugUnitTest

# Integration tests
./gradlew connectedAndroidTest

# All tests
./gradlew test
```

## 📊 Testing

### Test Coverage
- **Repository Tests**: API integration, error handling, network scenarios
- **ViewModel Tests**: State management, loading states, pagination
- **UI Tests**: Navigation, user interactions, accessibility
- **Utils Tests**: Date formatting, network utilities, extensions

### Test Structure
```
app/src/test/java/                 # Unit tests
app/src/androidTest/java/          # Integration tests
app/src/testShared/                # Shared test utilities
```

## 📂 Project Structure

```
app/src/main/java/com/viaductecho/android/
├── data/
│   ├── api/                       # Retrofit API interfaces
│   ├── models/                    # Data classes and DTOs
│   └── repository/                # Repository implementations
├── ui/
│   ├── articles/                  # Article list and detail screens
│   ├── common/                    # Reusable UI components
│   └── main/                      # Main activity and navigation
├── utils/                         # Utility classes and extensions
└── ViaductEchoApplication.kt      # Application class
```

## 🎯 Key Components

### ArticleListFragment
- Displays paginated list of articles
- Implements endless scroll with loading indicators
- Pull-to-refresh functionality
- Empty states and error handling

### ArticleDetailFragment
- Full article content display
- AI summary highlighting with purple theme
- Share functionality
- External link to original article

### ArticleRepository
- Centralized data access layer
- Error handling with Resource wrapper
- Network connectivity awareness
- Optional offline caching

## 🔧 Configuration

### Build Configuration
- **minSdk**: 24 (Android 7.0)
- **targetSdk**: 34 (Android 14)
- **compileSdk**: 34
- **Java Version**: 1.8
- **Kotlin Version**: 1.9+

### ProGuard Rules
Optimized for release builds with:
- Retrofit and Gson preservation
- Glide optimization
- Custom model class retention

### Performance Optimizations
- R8 full mode enabled
- Build cache enabled
- Incremental compilation
- Parallel builds
- Configuration cache

## 🚀 Deployment

### Debug Deployment
1. Connect Android device or start emulator
2. Run `./gradlew installDebug`
3. Launch "Viaduct Echo" app

### Release Deployment
1. Generate signed APK: `./gradlew assembleRelease`
2. Upload to Play Console or distribute APK
3. Monitor crash reports and performance

### CI/CD Integration
The project includes GitHub Actions workflows for:
- Automated testing on PRs
- Release builds for tags
- Code quality checks with detekt
- Dependency vulnerability scanning

## 🔍 Troubleshooting

### Common Issues

**Network Errors**:
- Check API server is running
- Verify API_BASE_URL configuration
- Ensure device has internet connectivity

**Build Failures**:
- Clean project: `./gradlew clean`
- Invalidate caches in Android Studio
- Check Gradle and plugin versions

**Emulator Issues**:
- Use `10.0.2.2:8000` for localhost API
- Enable internet in AVD settings
- Check firewall settings

### Debug Tools
- **Network Inspector**: Monitor API calls in Android Studio
- **Memory Profiler**: Check for memory leaks
- **Layout Inspector**: Verify UI hierarchy
- **Accessibility Scanner**: Test accessibility compliance

## 📈 Performance Metrics

### Target Benchmarks
- **App Launch**: < 2 seconds cold start
- **List Scrolling**: 60 FPS with images
- **Memory Usage**: < 100MB during normal operation
- **Network Efficiency**: 80% cache hit rate for images

### Monitoring
- Crashlytics for crash reporting
- Performance monitoring with Firebase
- Custom analytics for user engagement
- Memory leak detection with LeakCanary

## 🤝 Contributing

1. Follow Android coding conventions
2. Write comprehensive tests for new features
3. Ensure accessibility compliance
4. Update documentation for changes
5. Test on multiple devices and API levels

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For issues related to the Android app:
- Create GitHub Issues with detailed reproduction steps
- Include device model, Android version, and app version
- Attach relevant logs from Logcat if possible