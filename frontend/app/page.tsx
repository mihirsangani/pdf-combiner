import { Hero } from '@/components/home/hero'
import { Features } from '@/components/home/features'
import { Tools } from '@/components/home/tools'
import { HowItWorks } from '@/components/home/how-it-works'
import { CTA } from '@/components/home/cta'

export default function HomePage() {
  return (
    <>
      <Hero />
      <Features />
      <Tools />
      <HowItWorks />
      <CTA />
    </>
  )
}
