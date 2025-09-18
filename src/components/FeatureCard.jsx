function FeatureCard({ title, description, shape }) {
  const renderShape = () => {
    switch(shape) {
      case "circle":
        return <div className="w-16 h-16 rounded-full border-2 border-black mx-auto mb-6"></div>;
      case "square":
        return <div className="w-16 h-16 border-2 border-black mx-auto mb-6"></div>;
      case "triangle":
        return (
          <div className="w-16 h-16 mx-auto mb-6 relative">
            <div className="absolute inset-0 border-l-2 border-r-2 border-b-2 border-black transform rotate-45"></div>
          </div>
        );
      default:
        return <div className="w-16 h-16 border-2 border-black mx-auto mb-6"></div>;
    }
  };

  return (
    <div className="text-center p-8 border border-gray-200 rounded-sm">
      {renderShape()}
      <h4 className="text-xl font-semibold mb-4">{title}</h4>
      <p className="text-gray-700">{description}</p>
    </div>
  );
}

export default FeatureCard;