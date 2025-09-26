# Add project specific ProGuard rules here.
# You can control the set of applied configuration files using the
# proguardFiles setting in build.gradle.

# Keep line numbers for debugging stack traces
-keepattributes SourceFile,LineNumberTable

# Retrofit
-keepattributes Signature, InnerClasses, EnclosingMethod
-keepattributes RuntimeVisibleAnnotations, RuntimeVisibleParameterAnnotations
-keepclassmembers,allowshrinking,allowobfuscation interface * {
    @retrofit2.http.* <methods>;
}
-dontwarn org.codehaus.mojo.animal_sniffer.IgnoreJRERequirement
-dontwarn javax.annotation.**
-dontwarn kotlin.Unit
-dontwarn retrofit2.KotlinExtensions
-dontwarn retrofit2.KotlinExtensions*

# Gson
-keepattributes Signature
-keepattributes *Annotation*
-dontwarn sun.misc.**
-keep class com.google.gson.** { *; }
-keep class * implements com.google.gson.TypeAdapterFactory
-keep class * implements com.google.gson.JsonSerializer
-keep class * implements com.google.gson.JsonDeserializer

# Keep data classes and all their generic signatures
-keep class com.viaductecho.android.data.models.** { *; }
-keepclassmembers class com.viaductecho.android.data.models.** {
    *;
}

# Fix ParameterizedType casting issues
-keepattributes Signature,RuntimeVisibleAnnotations,AnnotationDefault
-keep class java.lang.reflect.ParameterizedType { *; }
-keep class java.lang.reflect.Type { *; }
-keep class java.lang.reflect.WildcardType { *; }
-keep class java.lang.reflect.GenericArrayType { *; }

# Enhanced Gson rules for generic types
-keep class com.google.gson.reflect.TypeToken { *; }
-keep class * extends com.google.gson.reflect.TypeToken
-keepclassmembers,allowobfuscation class * {
  @com.google.gson.annotations.SerializedName <fields>;
}

# Hilt rules
-keep class dagger.hilt.** { *; }
-keep class javax.inject.** { *; }
-keep class * extends dagger.hilt.android.HiltAndroidApp
-keepclasseswithmembers class * {
    @dagger.hilt.android.AndroidEntryPoint <methods>;
}
-keep @dagger.hilt.android.AndroidEntryPoint class * {
    *;
}

# Glide
-keep public class * implements com.bumptech.glide.module.GlideModule
-keep class * extends com.bumptech.glide.module.AppGlideModule {
 <init>(...);
}
-keep public enum com.bumptech.glide.load.ImageHeaderParser$** {
  **[] $VALUES;
  public *;
}

# Additional safety rules for API responses
-keep class com.viaductecho.android.** { *; }
-keepclassmembers class com.viaductecho.android.** {
    <fields>;
    <methods>;
}

# Prevent obfuscation of API response classes
-keep class * extends java.lang.Object {
    @com.google.gson.annotations.* <fields>;
}

# Retrofit response types
-keep,allowobfuscation,allowshrinking interface retrofit2.Call
-keep,allowobfuscation,allowshrinking class retrofit2.Response
-keep,allowobfuscation,allowshrinking class kotlin.collections.List
