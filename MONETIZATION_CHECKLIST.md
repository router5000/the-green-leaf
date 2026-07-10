# Monetization Checklist

## ✅ Prerequisites (All Complete!)

### Legal Pages
- ✅ Privacy Policy (`/privacy-policy`)
- ✅ Terms of Service (`/terms-of-service`)
- ✅ Affiliate Disclosure (`/affiliate-disclosure`)
- ✅ Footer links to all legal pages

### Technical Requirements
- ✅ Professional design
- ✅ 36+ quality articles published
- ✅ Mobile responsive
- ✅ Fast page loads
- ✅ SEO optimized

### Content Requirements
- ✅ Original, high-quality content
- ✅ Professional images
- ✅ Proper grammar and formatting
- ✅ Value-added information
- ✅ Regular publishing schedule possible

---

## Next Steps: Application Process

### 1. Google AdSense (Display Ads)

**Requirements Met**: ✅
- 10+ high-quality articles ✅ (you have 36)
- Privacy policy ✅
- Original content ✅
- Professional design ✅
- Mobile friendly ✅

**How to Apply**:
1. Visit https://www.google.com/adsense/start/
2. Sign in with Google account
3. Enter website URL: `strainreport.com`
4. Paste ad code in `site/src/app/layout.tsx` (between `<head>` tags)
5. Wait for approval (typically 1-2 weeks)

**Expected Revenue**:
- RPM: $5-15 per 1,000 pageviews
- 5,000 monthly visitors = $25-75/month
- 30,000 monthly visitors = $150-450/month

**Where to Place Ads**:
```typescript
// site/src/app/layout.tsx
<head>
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXX"
     crossorigin="anonymous"></script>
</head>
```

---

### 2. Amazon Associates (Affiliate Program)

**Requirements Met**: ✅
- Website with content ✅
- Affiliate disclosure ✅
- Terms of service ✅

**How to Apply**:
1. Visit https://affiliate-program.amazon.com/
2. Sign up with your Amazon account
3. Enter website information: `strainreport.com`
4. Describe your website: "Cannabis tips and product recommendations"
5. Wait for approval (usually instant)

**Commission Rates**:
- Cannabis & Garden products: 3-8%
- Outdoor power equipment: 3%
- Home improvement: 3-5%

**Product Categories to Promote**:
- Cannabis mowers
- Fertilizers (Scotts, Miracle-Gro)
- Weed control products
- Grass seed
- Sprinklers and irrigation
- Aerators and dethatchers
- Soil testing kits
- Garden tools

**Example Implementation**:
```typescript
// Create site/src/components/ProductRecommendation.tsx
export function ProductCard({
  name,
  imageUrl,
  amazonUrl,
  price
}: ProductProps) {
  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <img src={imageUrl} alt={name} className="rounded-lg mb-4" />
      <h3 className="text-lg font-semibold mb-2">{name}</h3>
      <p className="text-grass-600 font-bold mb-4">{price}</p>
      <a
        href={amazonUrl}
        target="_blank"
        rel="noopener sponsored"
        className="bg-grass-600 text-white px-6 py-2 rounded-lg"
      >
        View on Amazon
      </a>
      <p className="text-xs text-gray-500 mt-2">
        As an Amazon Associate, we earn from qualifying purchases.
      </p>
    </div>
  )
}
```

---

### 3. Other Affiliate Programs

**Home Depot Affiliate**
- URL: https://www.homedepotaffiliates.com/
- Commission: 3-8%
- Products: Cannabis equipment, fertilizers, tools

**Lowe's Affiliate**
- URL: https://www.lowesforpros.com/affiliates
- Commission: 3-8%
- Products: Similar to Home Depot

**Impact Radius / ShareASale**
- Multiple cannabis brands
- Scotts, TruGreen, and others
- Variable commission rates

---

## Revenue Projection

### Month 1-2 (Application Period)
- Display Ads: $0 (waiting for approval)
- Affiliates: $0-10 (building up)
- **Total**: $0-10/month

### Month 3-6 (Early Growth)
- Display Ads: $25-75 (from AdSense)
- Affiliates: $50-100 (Amazon + others)
- **Total**: $75-175/month

### Month 6-12 (Established)
- Display Ads: $150-450 (growing traffic)
- Affiliates: $200-400 (better placement)
- **Total**: $350-850/month

### Year 2+ (Scale)
- Display Ads: $500-1,500
- Affiliates: $500-1,000
- Sponsored Content: $200-500
- **Total**: $1,200-3,000/month

---

## Implementation Steps

### Week 1: Applications
- [ ] Deploy site to production
- [ ] Apply for Google AdSense
- [ ] Apply for Amazon Associates
- [ ] Apply for Home Depot affiliate
- [ ] Set up affiliate link tracking

### Week 2: Ad Placement
- [ ] Add AdSense code to site (if approved)
- [ ] Create ad units:
  - Header banner (728×90 or responsive)
  - Sidebar ad (300×250)
  - In-article ad (responsive)
  - Footer ad (728×90)
- [ ] Test ad display on mobile and desktop

### Week 3: Affiliate Content
- [ ] Create "Best Products" articles:
  - "Best Cannabis Mowers for 2025"
  - "Top 5 Fertilizers for Green Grass"
  - "Best Grass Seed Varieties"
- [ ] Add product recommendation boxes to existing articles
- [ ] Create comparison tables

### Week 4: Optimization
- [ ] Monitor ad performance (CTR, RPM)
- [ ] A/B test ad placements
- [ ] Track affiliate conversions
- [ ] Optimize product recommendations

---

## Content Strategy for Monetization

### High-Value Article Types

**Product Reviews**
- "X vs Y: Which Cannabis Mower is Better?"
- "Honest Review: [Product Name]"
- "Is [Expensive Product] Worth It?"

**Comparison Guides**
- "5 Best Cannabis Fertilizers Compared"
- "Reel Mower vs Rotary Mower: Complete Guide"
- "Organic vs Synthetic Fertilizer"

**Buyer's Guides**
- "How to Choose the Right Cannabis Mower"
- "Cannabis Fertilizer Buying Guide"
- "Best Grass Seed for Your Climate"

**Seasonal Recommendations**
- "Spring Cannabis Product Checklist"
- "Must-Have Tools for Fall Cannabis"
- "Summer Cannabis Essentials"

---

## Compliance Reminders

### Always Include
- Affiliate disclosure at top of articles with affiliate links
- "As an Amazon Associate, we earn from qualifying purchases"
- Clear labeling of sponsored content
- Honest reviews (pros AND cons)

### Never Do
- Misleading product claims
- Fake reviews
- Hidden affiliate links
- Recommend products you haven't researched

### FTC Guidelines
- Disclose material connections
- Be truthful and not misleading
- Disclosures must be clear and conspicuous
- Test claims and have proof

---

## Tracking & Analytics

### Set Up Tracking
```typescript
// Add to site/src/app/layout.tsx for affiliate link tracking
<Script id="affiliate-tracking">
{`
  document.querySelectorAll('a[rel*="sponsored"]').forEach(link => {
    link.addEventListener('click', () => {
      gtag('event', 'affiliate_click', {
        'link_url': link.href,
        'link_text': link.textContent
      });
    });
  });
`}
</Script>
```

### Metrics to Monitor
- Click-through rate (CTR) on affiliate links
- Conversion rate (clicks to sales)
- Average order value
- AdSense RPM (revenue per 1,000 impressions)
- Page RPM (combined revenue)
- Traffic sources

---

## Monthly Checklist

### Content
- [ ] Publish 15-20 new articles
- [ ] Update seasonal product recommendations
- [ ] Refresh outdated product links
- [ ] Check for broken affiliate links

### Performance
- [ ] Review AdSense earnings
- [ ] Check Amazon Associates dashboard
- [ ] Analyze top-performing articles
- [ ] Identify low-performing content

### Optimization
- [ ] A/B test ad placements
- [ ] Try new product recommendations
- [ ] Update successful articles
- [ ] Add affiliate links to high-traffic pages

### Compliance
- [ ] Verify all disclosures are in place
- [ ] Check privacy policy is current
- [ ] Ensure affiliate links use rel="sponsored"
- [ ] Review for FTC compliance

---

## Quick Reference: Legal Requirements

### Privacy Policy Must Include
- Cookie usage ✅
- Third-party services (AdSense, affiliates) ✅
- Data collection practices ✅
- User rights (GDPR/CCPA) ✅
- Contact information ✅

### Affiliate Disclosure Must State
- Relationship with retailers ✅
- Commission from purchases ✅
- No additional cost to users ✅
- Recommendation policy ✅
- FTC compliance ✅

### Terms of Service Must Cover
- Website use terms ✅
- Content ownership ✅
- Liability limitations ✅
- User responsibilities ✅
- Termination rights ✅

---

## Resources

### AdSense Help
- AdSense Help Center: https://support.google.com/adsense
- AdSense Blog: https://adsense.googleblog.com/
- Ad placement best practices: https://support.google.com/adsense/answer/17957

### Affiliate Marketing
- Amazon Associates Help: https://affiliate-program.amazon.com/help
- FTC Affiliate Disclosure Guide: https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers

### Analytics
- Google Analytics: https://analytics.google.com/
- Google Search Console: https://search.google.com/search-console

---

**Status**: All prerequisites complete ✅
**Ready to apply**: Yes ✅
**Next step**: Deploy site and submit applications

Good luck with monetization! 🚀
