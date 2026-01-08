'use client'

import { motion } from 'framer-motion'
import { Upload, Settings, Download, CheckCircle2 } from 'lucide-react'

const steps = [
  {
    name: 'Upload Files',
    description: 'Drag and drop your files or click to browse',
    icon: Upload,
  },
  {
    name: 'Configure',
    description: 'Choose your settings and preferences',
    icon: Settings,
  },
  {
    name: 'Process',
    description: 'We handle the processing automatically',
    icon: CheckCircle2,
  },
  {
    name: 'Download',
    description: 'Get your processed files instantly',
    icon: Download,
  },
]

export function HowItWorks() {
  return (
    <section className="py-20 md:py-32">
      <div className="container">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mx-auto max-w-2xl text-center"
        >
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            How It Works
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Four simple steps to process your files
          </p>
        </motion.div>

        <div className="mt-16">
          <div className="grid gap-8 md:grid-cols-4">
            {steps.map((step, index) => (
              <motion.div
                key={step.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="relative text-center"
              >
                {/* Connector line (hidden on last item) */}
                {index < steps.length - 1 && (
                  <div className="absolute left-1/2 top-8 hidden h-0.5 w-full bg-border md:block" />
                )}

                {/* Icon */}
                <div className="relative mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary text-primary-foreground">
                  <step.icon className="h-8 w-8" />
                  <div className="absolute -bottom-2 -right-2 flex h-8 w-8 items-center justify-center rounded-full bg-background text-sm font-bold text-primary ring-2 ring-background">
                    {index + 1}
                  </div>
                </div>

                {/* Content */}
                <h3 className="mb-2 text-lg font-semibold">{step.name}</h3>
                <p className="text-sm text-muted-foreground">{step.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
