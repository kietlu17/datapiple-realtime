import scrapy
from goodread.items import GoodreadItem


class GoodreadcrawlSpider(scrapy.Spider):
    name = "goodreadcrawl"
    allowed_domains = ["goodreads.com"]

    def start_requests(self):
        self.page_number = 0
        yield scrapy.Request(url='https://goodreads.com/list/show/19.Best_for_Book_Clubs', callback=self.parse)
        
    def parse(self, response):
        self.logger.info('Parsing main page...')
        book_links = response.xpath('//a[contains(@class, "bookTitle")]/@href').getall()
        numbers = response.xpath('//td[@class="number"]/text()').getall()
        self.logger.info(f'Found {len(book_links)} book links')

        for i, (book_item, number) in enumerate(zip(book_links, numbers)):
            item = GoodreadItem()
            item['bookUrl'] = response.urljoin(book_item)
            item['number'] = i + 1 + self.page_number * 100
            score = response.xpath(f'(//span[@class="smallText uitext"]/a[1]/text())[{i+1}]').get()
            votes = response.xpath(f'(//span[@class="smallText uitext"]/a[2]/text())[{i+1}]').get()
            
            item['score'] = score
            item['votes'] = votes
            self.logger.info(f'Processing book URL: {item["bookUrl"]} with number {item["number"]}')
            request = scrapy.Request(url=item['bookUrl'], callback=self.parseBookDetailPage)
            request.meta['datacourse'] = item
            yield request
        
        next_page = response.xpath('//a[@class="next_page"]/@href').get()
        if next_page and self.page_number < 19:
            self.page_number += 1   
            self.logger.info(f'Found next page: {next_page}')
            yield scrapy.Request(url=response.urljoin(next_page), callback=self.parse)
            
    def parseBookDetailPage(self, response):
        item = response.meta['datacourse']
       # Lấy thông tin sách từ trang chi tiết
        item['bookname'] = response.xpath('normalize-space(//h1[@class="Text Text__title1"]/text())').get()
        item['author'] = response.xpath('normalize-space(//span[@class="ContributorLink__name"]/text())').get()
        item['authorUrl'] = response.xpath('//a[@class="ContributorLink"]/@href').get()
        item['prices'] = response.xpath('//*[@id="__next"]/div[2]/main/div[1]/div[1]/div/div[2]/div[2]/div/div[1]/button/span[1]/text()').get()
        item['genre'] = response.xpath('//span[@class="BookPageMetadataSection__genreButton"]//a//span/text()').get()   
        description = response.xpath('normalize-space(string(//span[@class="Formatted"]))').get()   
        item['describe'] = ''.join(description)
        item['rating'] = response.xpath('//div[@class="RatingStatistics__rating"]/text()').get()
        # Xử lý số lượng đánh giá
        ratings_count = response.xpath('//span[@data-testid="ratingsCount"]/text()').get()
        item['ratingcount'] = ''.join(ratings_count)
        reviews = response.xpath('//span[@data-testid="reviewsCount"]/text()').get()
        item['reviews'] = ''.join(reviews)
        # Số lượng sao đánh giá
        item['fivestars'] = response.xpath('//div[@data-testid="labelTotal-5"]/text()').get()
        item['fourstars'] = response.xpath('//div[@data-testid="labelTotal-4"]/text()').get()
        item['threestars'] = response.xpath('//div[@data-testid="labelTotal-3"]/text()').get()
        item['twostars'] = response.xpath('//div[@data-testid="labelTotal-2"]/text()').get()
        item['onestar'] = response.xpath('//div[@data-testid="labelTotal-1"]/text()').get()
        item['pages'] = response.xpath('//p[@data-testid="pagesFormat"]/text()').get()
        item['publish'] = response.xpath('//p[@data-testid="publicationInfo"]/text()').get()
        yield item