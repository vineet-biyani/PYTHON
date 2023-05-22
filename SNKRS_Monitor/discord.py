from discord_webhook import DiscordWebhook, DiscordEmbed

def hook(product_title, image_url, url, website, category, price, model, stock_status, size_stock, colors) :

    webhook = DiscordWebhook(url = 'YOUR_DISCORD_WEBHOOK_LINK',
                            username = "SNKRS")

    embed = DiscordEmbed(title = product_title,  url = url, color = '03b2f8')

    embed.set_author(name = 'Nike_SNKRS',
                    icon_url = 'https://i.pinimg.com/originals/29/c2/e8/29c2e883fb280a99a669fddc80df9088.jpg')

    embed.set_thumbnail(url = image_url)

    embed.set_timestamp()

    embed.add_embed_field(name = 'Stock Status', value = stock_status)

    embed.add_embed_field(name = 'Price', value = price + ' USD')

    embed.add_embed_field(name = 'Category', value = category)

    embed.add_embed_field(name = 'Site', value = website)

    embed.add_embed_field(name = 'Region', value = 'United States')

    embed.add_embed_field(name = 'Model', value = 'Model' + ' ' + model)

    embed.add_embed_field(name='Sizes', value = size_stock)

    embed.add_embed_field(name = 'Colors', value = colors)

    embed.set_footer(text = 'SNKRS Monitor v0.1')

    webhook.add_embed(embed)
    response = webhook.execute()
