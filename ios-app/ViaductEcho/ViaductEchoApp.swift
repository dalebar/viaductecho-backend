import SwiftUI

@main
struct ViaductEchoApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(APIService.shared)
        }
    }
}
