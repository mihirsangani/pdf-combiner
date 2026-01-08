'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import {
  FileText,
  Merge,
  Split,
  Minimize2,
  Image,
  FileImage,
  FileSpreadsheet,
  Repeat,
} from 'lucide-react'

const tools = [
  {
    name: 'Merge PDFs',
    description: 'Combine multiple PDF files into one document',
    icon: Merge,
    href: '/tools/pdf-merge',
    color: 'from-blue-500 to-cyan-500',
  },
  {
    name: 'Split PDF',
    description: 'Extract pages or split PDF into multiple files',
    icon: Split,
    href: '/tools/pdf-split',
    color: 'from-purple-500 to-pink-500',
  },
  {
    name: 'Compress PDF',
    description: 'Reduce PDF file size while maintaining quality',
    icon: Minimize2,
    href: '/tools/pdf-compress',
    color: 'from-orange-500 to-red-500',
  },
  {
    name: 'PDF to Word',
    description: 'Convert PDF documents to editable Word files',
    icon: FileText,
    href: '/tools/pdf-to-word',
    color: 'from-green-500 to-emerald-500',
  },
  {
    name: 'Word to PDF',
    description: 'Convert Word documents to PDF format',
    icon: FileSpreadsheet,
    href: '/tools/word-to-pdf',
    color: 'from-indigo-500 to-blue-500',
  },
  {
    name: 'PDF to Image',
    description: 'Extract images or convert PDF pages to images',
    icon: FileImage,
    href: '/tools/pdf-to-image',
    color: 'from-yellow-500 to-orange-500',
  },
  {
    name: 'Image to PDF',
    description: 'Convert images to PDF documents',
    icon: Image,
    href: '/tools/image-to-pdf',
    color: 'from-teal-500 to-green-500',
  },
  {
    name: 'Convert Images',
    description: 'Convert between different image formats',
    icon: Repeat,
    href: '/tools/image-convert',
    color: 'from-pink-500 to-rose-500',
  },
]

export function Tools() {
  return (
    <section className="bg-muted/50 py-20 md:py-32">
      <div className="container">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mx-auto max-w-2xl text-center"
        >
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Powerful Tools at Your Fingertips
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Professional file processing tools for every need
          </p>
        </motion.div>

        <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {tools.map((tool, index) => (
            <motion.div
              key={tool.name}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.05 }}
            >
              <Link
                href={tool.href}
                className="group relative block overflow-hidden rounded-2xl border bg-card p-6 shadow-sm transition-all hover:shadow-xl"
              >
                {/* Gradient background */}
                <div
                  className={`absolute inset-0 bg-gradient-to-br ${tool.color} opacity-0 transition-opacity group-hover:opacity-10`}
                />

                {/* Icon */}
                <div className="mb-4 inline-flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br from-primary/10 to-primary/5">
                  <tool.icon className="h-7 w-7 text-primary" />
                </div>

                {/* Content */}
                <h3 className="mb-2 text-lg font-semibold group-hover:text-primary">
                  {tool.name}
                </h3>
                <p className="text-sm text-muted-foreground">{tool.description}</p>

                {/* Arrow indicator */}
                <div className="mt-4 flex items-center text-sm font-medium text-primary opacity-0 transition-opacity group-hover:opacity-100">
                  Try now →
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
