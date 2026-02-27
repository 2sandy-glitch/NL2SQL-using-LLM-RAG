export const SAMPLE_SCHEMA = `-- Paste your schema here or upload a .sql file
CREATE TABLE customers (
  customer_id INT PRIMARY KEY,
  name VARCHAR(100),
  email VARCHAR(100),
  created_at TIMESTAMP
);

CREATE TABLE orders (
  order_id INT PRIMARY KEY,
  customer_id INT REFERENCES customers(customer_id),
  order_date TIMESTAMP,
  total_amount DECIMAL(10,2),
  status VARCHAR(20)
);

CREATE TABLE products (
  product_id INT PRIMARY KEY,
  product_name VARCHAR(100),
  category VARCHAR(50),
  price DECIMAL(10,2)
);

CREATE TABLE order_items (
  item_id INT PRIMARY KEY,
  order_id INT REFERENCES orders(order_id),
  product_id INT REFERENCES products(product_id),
  quantity INT,
  unit_price DECIMAL(10,2)
);

CREATE TABLE employees (
  employee_id INT PRIMARY KEY,
  first_name VARCHAR(50),
  last_name VARCHAR(50),
  department_id INT,
  hire_date DATE,
  job_title VARCHAR(100)
);

CREATE TABLE departments (
  department_id INT PRIMARY KEY,
  department_name VARCHAR(100)
);`;

export function parseSchema(schemaText) {
    const tables = {};
    const tableRegex = /CREATE TABLE\s+(\w+)\s*\(([^;]+)\)/gi;
    let match;
    while ((match = tableRegex.exec(schemaText)) !== null) {
        const tableName = match[1];
        const columnBlock = match[2];
        const columns = [];
        for (const line of columnBlock.split("\n")) {
            const trimmed = line.trim();
            if (!trimmed || trimmed.startsWith("--") || /^(PRIMARY|FOREIGN|UNIQUE|INDEX|CONSTRAINT)/i.test(trimmed)) continue;
            const colMatch = trimmed.match(/^(\w+)\s+(\w+)/);
            if (colMatch) columns.push({ name: colMatch[1], type: colMatch[2].toUpperCase() });
        }
        tables[tableName] = columns;
    }
    return tables;
}
