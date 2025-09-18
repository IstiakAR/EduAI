function TestimonialCard({ quote, author }) {
  return (
    <div className="p-6 border border-gray-200 rounded-sm">
      <div className="text-4xl font-serif mb-4">"</div>
      <p className="text-gray-700 mb-4">{quote}</p>
      <p className="font-semibold">{author}</p>
    </div>
  );
}

export default TestimonialCard;