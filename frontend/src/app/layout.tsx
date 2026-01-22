import type { Metadata } from 'next'
import { Outfit } from 'next/font/google'
import './globals.css'
import { AuthProvider } from '@/contexts/AuthContext'
import { Toaster } from 'react-hot-toast'
import Header from '@/components/Header'

const outfit = Outfit({
  subsets: ['latin'],
  variable: '--font-outfit',
})

export const metadata: Metadata = {
  title: 'StudyBuddy - AI-Powered Study Companion',
  description: 'Transform your study materials into comprehensive learning resources with AI',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={outfit.variable}>
      <body className={outfit.className}>
        <AuthProvider>
          {/* Animated Background */}
          <div className="fixed inset-0 -z-10 overflow-hidden">
            {/* Gradient Base */}
            <div className="absolute inset-0 bg-gradient-to-br from-pink-50 via-fuchsia-50 to-purple-50" />

            {/* Floating Blobs */}
            <div className="floating-blob w-96 h-96 bg-pink-300/40 top-0 -left-48 animation-delay-0" />
            <div className="floating-blob w-[500px] h-[500px] bg-fuchsia-300/30 top-1/4 -right-64 animation-delay-200" />
            <div className="floating-blob w-80 h-80 bg-purple-300/30 bottom-0 left-1/4 animation-delay-500" />
            <div className="floating-blob w-64 h-64 bg-rose-300/40 bottom-1/4 right-1/4 animation-delay-700" />

            {/* Grid Pattern Overlay */}
            <div
              className="absolute inset-0 opacity-[0.03]"
              style={{
                backgroundImage: `linear-gradient(rgba(236, 72, 153, 0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(236, 72, 153, 0.5) 1px, transparent 1px)`,
                backgroundSize: '50px 50px'
              }}
            />
          </div>

          <div className="relative min-h-screen">
            <Header />
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
              {children}
            </main>
          </div>

          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: 'rgba(255, 255, 255, 0.9)',
                backdropFilter: 'blur(16px)',
                border: '1px solid rgba(236, 72, 153, 0.2)',
                boxShadow: '0 10px 40px rgba(236, 72, 153, 0.15)',
                borderRadius: '16px',
                color: '#be185d',
                fontWeight: '500',
              },
              success: {
                iconTheme: {
                  primary: '#10b981',
                  secondary: '#fff',
                },
              },
              error: {
                iconTheme: {
                  primary: '#f43f5e',
                  secondary: '#fff',
                },
              },
            }}
          />
        </AuthProvider>
      </body>
    </html>
  )
}
