'use client'

import { motion } from 'framer-motion'
import { Shield, Zap, Lock, Cloud, Users, Sparkles } from 'lucide-react'

const features = [
  {
    name: 'Lightning Fast',
    description: 'Process files in seconds with our optimized infrastructure and cutting-edge algorithms.',
    icon: Zap,
  },
  {
    name: 'Secure & Private',
    description: 'End-to-end encryption. Files are automatically deleted after 24 hours.',
    icon: Shield,
  },
  {
    name: 'Bank-Level Security',
    description: '256-bit SSL encryption ensures your files are safe during transfer and processing.',
    icon: Lock,
  },
  {
    name: 'Cloud Storage Ready',
    description: 'Seamlessly integrate with popular cloud storage providers for easy file management.',
    icon: Cloud,
  },
  {
    name: 'Team Collaboration',
    description: 'Share files and collaborate with your team in real-time with advanced permissions.',
    icon: Users,
  },
  {
    name: 'AI-Powered',
    description: 'Smart file optimization and compression using advanced AI algorithms.',
    icon: Sparkles,
  },
]

export function Features() {
  return (
    <section id="features" className="py-20 md:py-32">
      <div className="container">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="mx-auto max-w-2xl text-center"
        >
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Everything You Need
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Professional-grade features designed for individuals and enterprises
          </p>
        </motion.div>

        <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => (
            <motion.div
              key={feature.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className="group relative overflow-hidden rounded-2xl border bg-card p-8 shadow-sm transition-all hover:shadow-lg"
            >
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <feature.icon className="h-6 w-6" />
              </div>
              <h3 className="mb-2 text-xl font-semibold">{feature.name}</h3>
              <p className="text-muted-foreground">{feature.description}</p>
              
              {/* Hover effect */}
              <div className="absolute inset-0 -z-10 bg-gradient-to-br from-primary/5 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
