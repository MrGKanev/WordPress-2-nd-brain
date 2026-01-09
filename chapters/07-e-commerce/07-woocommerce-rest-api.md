# WooCommerce REST API

The WooCommerce REST API allows external access to your store - for mobile apps, ERP integrations, or headless frontend.

## API Overview

### Base URL

```
https://yoursite.com/wp-json/wc/v3/
```

### Versions

| Version | Status |
|---------|--------|
| v1 | Deprecated |
| v2 | Legacy |
| v3 | Current (recommended) |

## Authentication

### REST API Keys

```
WooCommerce > Settings > Advanced > REST API > Add key

Description: My App
User: admin
Permissions: Read/Write
```

You receive:
- Consumer Key (ck_...)
- Consumer Secret (cs_...)

### Authentication Methods

**1. HTTP Basic Auth (HTTPS required)**

```bash
curl https://yoursite.com/wp-json/wc/v3/products \
  -u ck_xxx:cs_xxx
```

**2. Query String (testing only)**

```
https://yoursite.com/wp-json/wc/v3/products?consumer_key=ck_xxx&consumer_secret=cs_xxx
```

**3. OAuth 1.0a (for non-HTTPS)**

More complex, requires signature. Use a library.

## Products API

### List Products

```bash
GET /wp-json/wc/v3/products

# With filters
GET /wp-json/wc/v3/products?category=123&per_page=20&page=1
GET /wp-json/wc/v3/products?status=publish&stock_status=instock
GET /wp-json/wc/v3/products?sku=ABC123
```

### Get Single Product

```bash
GET /wp-json/wc/v3/products/{id}
```

Response:

```json
{
    "id": 123,
    "name": "Product Name",
    "slug": "product-name",
    "type": "simple",
    "status": "publish",
    "sku": "ABC123",
    "price": "29.99",
    "regular_price": "39.99",
    "sale_price": "29.99",
    "stock_quantity": 50,
    "stock_status": "instock",
    "categories": [
        {"id": 15, "name": "Clothing"}
    ],
    "images": [
        {"src": "https://..."}
    ],
    "meta_data": []
}
```

### Create Product

```bash
POST /wp-json/wc/v3/products

{
    "name": "New Product",
    "type": "simple",
    "regular_price": "49.99",
    "description": "Product description",
    "short_description": "Short desc",
    "categories": [{"id": 15}],
    "images": [
        {"src": "https://example.com/image.jpg"}
    ],
    "stock_quantity": 100,
    "manage_stock": true
}
```

### Update Product

```bash
PUT /wp-json/wc/v3/products/{id}

{
    "regular_price": "59.99",
    "stock_quantity": 75
}
```

### Delete Product

```bash
DELETE /wp-json/wc/v3/products/{id}?force=true
```

## Orders API

### List Orders

```bash
GET /wp-json/wc/v3/orders

# Filters
GET /wp-json/wc/v3/orders?status=processing
GET /wp-json/wc/v3/orders?after=2024-01-01T00:00:00&before=2024-12-31T23:59:59
GET /wp-json/wc/v3/orders?customer=5
```

### Get Order

```bash
GET /wp-json/wc/v3/orders/{id}
```

Response:

```json
{
    "id": 456,
    "status": "processing",
    "currency": "USD",
    "total": "129.99",
    "billing": {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone": "555-123-4567",
        "address_1": "123 Main St",
        "city": "Los Angeles",
        "postcode": "90001",
        "country": "US"
    },
    "shipping": {},
    "line_items": [
        {
            "id": 1,
            "product_id": 123,
            "quantity": 2,
            "total": "99.98"
        }
    ],
    "shipping_lines": [],
    "meta_data": []
}
```

### Update Order Status

```bash
PUT /wp-json/wc/v3/orders/{id}

{
    "status": "completed"
}
```

### Create Order (Manual)

```bash
POST /wp-json/wc/v3/orders

{
    "payment_method": "bacs",
    "payment_method_title": "Bank Transfer",
    "set_paid": false,
    "billing": {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "address_1": "123 Main St",
        "city": "Los Angeles",
        "postcode": "90001",
        "country": "US"
    },
    "line_items": [
        {
            "product_id": 123,
            "quantity": 2
        }
    ]
}
```

## Customers API

### List Customers

```bash
GET /wp-json/wc/v3/customers
GET /wp-json/wc/v3/customers?email=john@example.com
GET /wp-json/wc/v3/customers?role=customer
```

### Get Customer

```bash
GET /wp-json/wc/v3/customers/{id}
```

### Create Customer

```bash
POST /wp-json/wc/v3/customers

{
    "email": "new@example.com",
    "first_name": "New",
    "last_name": "Customer",
    "username": "newcustomer",
    "billing": {},
    "shipping": {}
}
```

## Categories & Tags

### List Categories

```bash
GET /wp-json/wc/v3/products/categories
```

### Create Category

```bash
POST /wp-json/wc/v3/products/categories

{
    "name": "New Category",
    "parent": 0,
    "image": {
        "src": "https://..."
    }
}
```

## Extending the API

### Add Custom Endpoint

```php
add_action( 'rest_api_init', function() {
    register_rest_route( 'custom/v1', '/stock-report', array(
        'methods'             => 'GET',
        'callback'            => 'get_stock_report',
        'permission_callback' => function() {
            return current_user_can( 'manage_woocommerce' );
        },
    ) );
} );

function get_stock_report( $request ) {
    $products = wc_get_products( array(
        'limit'        => -1,
        'stock_status' => 'outofstock',
    ) );

    $data = array();
    foreach ( $products as $product ) {
        $data[] = array(
            'id'    => $product->get_id(),
            'name'  => $product->get_name(),
            'sku'   => $product->get_sku(),
            'stock' => $product->get_stock_quantity(),
        );
    }

    return new WP_REST_Response( $data, 200 );
}
```

### Add Fields to Existing Endpoints

```php
// Add custom field to product response
add_filter( 'woocommerce_rest_prepare_product_object', function( $response, $product ) {
    $response->data['warehouse_location'] = $product->get_meta( '_warehouse_location' );
    $response->data['supplier_id'] = $product->get_meta( '_supplier_id' );
    return $response;
}, 10, 2 );

// Allow update of custom field
add_action( 'woocommerce_rest_insert_product_object', function( $product, $request ) {
    if ( isset( $request['warehouse_location'] ) ) {
        $product->update_meta_data( '_warehouse_location', sanitize_text_field( $request['warehouse_location'] ) );
        $product->save();
    }
}, 10, 2 );
```

### Modify Response Schema

```php
add_filter( 'woocommerce_rest_product_schema', function( $schema ) {
    $schema['properties']['warehouse_location'] = array(
        'description' => 'Warehouse location code',
        'type'        => 'string',
        'context'     => array( 'view', 'edit' ),
    );
    return $schema;
} );
```

## Webhooks

### Setting Up Webhooks

```
WooCommerce > Settings > Advanced > Webhooks > Add webhook

Name: Order Created
Status: Active
Topic: Order created
Delivery URL: https://yourapp.com/webhooks/woocommerce
Secret: your-secret-key
```

### Webhook Topics

| Topic | Trigger |
|-------|---------|
| order.created | New order |
| order.updated | Order changed |
| order.deleted | Order deleted |
| product.created | New product |
| product.updated | Product changed |
| customer.created | New customer |

### Webhook Payload Example

```json
{
    "id": 456,
    "status": "processing",
    "total": "129.99",
    "line_items": [],
    "_links": {}
}
```

### Verify Webhook Signature

```php
// In receiving endpoint
$payload = file_get_contents( 'php://input' );
$signature = $_SERVER['HTTP_X_WC_WEBHOOK_SIGNATURE'];
$secret = 'your-secret-key';

$expected = base64_encode( hash_hmac( 'sha256', $payload, $secret, true ) );

if ( ! hash_equals( $expected, $signature ) ) {
    http_response_code( 401 );
    die( 'Invalid signature' );
}

$data = json_decode( $payload, true );
// Process webhook...
```

## Batch Operations

### Batch Create/Update/Delete

```bash
POST /wp-json/wc/v3/products/batch

{
    "create": [
        {"name": "Product 1", "regular_price": "10"},
        {"name": "Product 2", "regular_price": "20"}
    ],
    "update": [
        {"id": 123, "regular_price": "15"}
    ],
    "delete": [456, 789]
}
```

**Limit:** Default 100 items per batch.

## Rate Limiting

WooCommerce doesn't have built-in rate limiting, but you can add it:

```php
add_filter( 'rest_pre_dispatch', function( $result, $server, $request ) {
    if ( strpos( $request->get_route(), '/wc/v3/' ) === false ) {
        return $result;
    }

    $ip = $_SERVER['REMOTE_ADDR'];
    $key = 'wc_api_rate_' . md5( $ip );
    $count = get_transient( $key ) ?: 0;

    if ( $count > 100 ) { // 100 requests per minute
        return new WP_Error(
            'rate_limit_exceeded',
            'Too many requests',
            array( 'status' => 429 )
        );
    }

    set_transient( $key, $count + 1, MINUTE_IN_SECONDS );
    return $result;
}, 10, 3 );
```

## PHP Client Example

```php
// Use official library
// composer require automattic/woocommerce

use Automattic\WooCommerce\Client;

$woocommerce = new Client(
    'https://yoursite.com',
    'ck_xxx',
    'cs_xxx',
    [
        'version' => 'wc/v3',
    ]
);

// Get products
$products = $woocommerce->get( 'products' );

// Create order
$order = $woocommerce->post( 'orders', [
    'payment_method' => 'bacs',
    'billing' => [],
    'line_items' => []
] );

// Update product stock
$woocommerce->put( 'products/123', [
    'stock_quantity' => 50
] );
```

## JavaScript Client Example

```javascript
// Using axios
const WooCommerce = {
    baseURL: 'https://yoursite.com/wp-json/wc/v3',
    auth: {
        username: 'ck_xxx',
        password: 'cs_xxx'
    }
};

// Get products
const products = await axios.get(`${WooCommerce.baseURL}/products`, {
    auth: WooCommerce.auth,
    params: { per_page: 20 }
});

// Create order
const order = await axios.post(`${WooCommerce.baseURL}/orders`, {
    payment_method: 'bacs',
    billing: {},
    line_items: []
}, { auth: WooCommerce.auth });
```

## Troubleshooting

### 401 Unauthorized

1. Check API keys are correct
2. Check HTTPS (Basic Auth requires SSL)
3. Check user has proper permissions

### 403 Forbidden

```php
// Check permission callback
// REST API might be disabled
add_filter( 'woocommerce_rest_check_permissions', function( $permission, $context, $object_id, $post_type ) {
    // Debug
    error_log( "Permission check: $context, $post_type, result: " . ($permission ? 'true' : 'false') );
    return $permission;
}, 10, 4 );
```

### Slow API Responses

```php
// Limit fields in response
GET /wp-json/wc/v3/products?_fields=id,name,price,stock_quantity

// Pagination
GET /wp-json/wc/v3/products?per_page=20&page=1
```

## Security Best Practices

1. **Always HTTPS** - never HTTP for API calls
2. **Minimum permissions** - read-only keys when possible
3. **IP Whitelist** - if API is used from known sources
4. **Rotate keys** - periodically change API keys
5. **Log API access** - monitor for suspicious activity
6. **Rate limiting** - prevent abuse

## Further Reading

- [WooCommerce Fundamentals](./01-woocommerce-fundamentals.md) - Data structures
- [WooCommerce Hooks](./02-woocommerce-hooks.md) - Extend via hooks
- [Official REST API Docs](https://woocommerce.github.io/woocommerce-rest-api-docs/)
- [WordPress REST API](https://developer.wordpress.org/rest-api/)
